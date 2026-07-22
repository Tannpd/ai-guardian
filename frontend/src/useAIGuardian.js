import { useState, useCallback, useEffect } from 'react';
import { createClient, createAccount } from 'genlayer-js';
import { studionet } from 'genlayer-js/chains';

const CONTRACT_ADDRESS = import.meta.env.VITE_CONTRACT_ADDRESS || '';

// Custom chain that proxies RPC through Vercel same-origin to bypass browser CORS policies
const getRpcEndpoint = () => {
  if (typeof window !== 'undefined' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
    return `${window.location.origin}/api/rpc`;
  }
  return 'https://studio.genlayer.com/api';
};

const customStudionet = {
  ...studionet,
  rpcUrls: {
    default: { http: [getRpcEndpoint()] },
    public: { http: [getRpcEndpoint()] },
  }
};

let _readClient = null;

function getReadClient() {
  if (!_readClient) {
    _readClient = createClient({ chain: customStudionet });
  }
  return _readClient;
}

function getWriteClient(account) {
  return createClient({ chain: customStudionet, account });
}

// Convert Wei (u256) to human readable GEN string
export function formatGen(weiVal) {
  if (!weiVal) return '0';
  try {
    const big = BigInt(weiVal);
    const integerPart = big / 10n**18n;
    const fractionalPart = big % 10n**18n;
    let fractionStr = fractionalPart.toString().padStart(18, '0');
    fractionStr = fractionStr.replace(/0+$/, ''); // Trim trailing zeros
    if (fractionStr === '') {
      return integerPart.toString();
    }
    return `${integerPart}.${fractionStr.slice(0, 4)}`;
  } catch (e) {
    return '0';
  }
}

// Convert human readable GEN input to Wei (u256 BigInt)
export function parseGen(genVal) {
  if (!genVal || genVal.toString().trim() === '') return 0n;
  try {
    const parts = genVal.toString().split('.');
    let integerPart = parts[0] || '0';
    let fractionalPart = parts[1] || '';
    fractionalPart = fractionalPart.slice(0, 18).padEnd(18, '0');
    return BigInt(integerPart) * 10n**18n + BigInt(fractionalPart);
  } catch (e) {
    return 0n;
  }
}

export function useAIGuardian() {
  const [address, setAddress] = useState('');
  const [glAccount, setGlAccount] = useState(null);
  const [guilds, setGuilds] = useState([]);
  const [contractBalance, setContractBalance] = useState('0');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [txHash, setTxHash] = useState('');
  const [txStatus, setTxStatus] = useState('');

  // Connect Wallet (MetaMask/ethereum provider or fallback ephemeral account)
  const connectWallet = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      if (typeof window !== 'undefined' && window.ethereum) {
        const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
        const addr = accounts[0].toLowerCase();
        setAddress(addr);
        setGlAccount(addr);
      } else {
        // Ephemeral account fallback
        let savedKey = localStorage.getItem('__aiguardian_sk');
        let acct;
        if (savedKey) {
          acct = createAccount(savedKey);
        } else {
          acct = createAccount();
          localStorage.setItem('__aiguardian_sk', acct.privateKey);
        }
        const addr = acct.address.toLowerCase();
        setAddress(addr);
        setGlAccount(acct);
      }
    } catch (err) {
      console.error('Wallet connection failed:', err);
      setError('Wallet connection failed: ' + err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch all guilds and contract balance
  const fetchGuildsState = useCallback(async () => {
    if (!CONTRACT_ADDRESS || CONTRACT_ADDRESS === '0x0000000000000000000000000000000000000000') return;
    setLoading(true);
    try {
      const client = getReadClient();
      
      // Get guilds count
      const rawCount = await client.readContract({
        address: CONTRACT_ADDRESS,
        functionName: 'get_guilds_count',
        args: [],
      });
      const count = Number(rawCount);
      
      const fetchedGuilds = [];
      for (let i = 0; i < count; i++) {
        const rawGuild = await client.readContract({
          address: CONTRACT_ADDRESS,
          functionName: 'get_guild',
          args: [i],
        });
        if (rawGuild && rawGuild !== '{}') {
          const guildObj = JSON.parse(rawGuild);
          fetchedGuilds.push(guildObj);
        }
      }
      
      // Get balance of contract (escrow pool balance)
      const rawBalance = await client.getBalance({ address: CONTRACT_ADDRESS });
      setContractBalance(rawBalance.toString());
      
      setGuilds(fetchedGuilds.reverse()); // Show newest first
      setError('');
    } catch (err) {
      console.error('Error fetching guilds:', err);
      setError('Failed to fetch guilds: ' + err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  // Create Guild (Lock GEN, set counsel and dataset name)
  const createGuild = async (counselAddress, datasetName, fundingAmt) => {
    if (!glAccount || !CONTRACT_ADDRESS) {
      throw new Error('Wallet not connected');
    }
    setLoading(true);
    setError('');
    setTxHash('');
    setTxStatus(`Funding Guild: locking ${fundingAmt} GEN for digital copyright defense...`);

    try {
      const client = getWriteClient(glAccount);
      const valueWei = parseGen(fundingAmt);
      
      const hash = await client.writeContract({
        address: CONTRACT_ADDRESS,
        functionName: 'create_guild',
        args: [counselAddress.trim(), datasetName.trim()],
        value: valueWei,
      });
      
      setTxHash(hash);
      setTxStatus('Submitting guild escrow creation transaction. Locking funds...');

      const receipt = await client.waitForTransactionReceipt({ hash });
      
      const leaderReceipt = receipt.consensus_data?.leader_receipt?.[0];
      if (leaderReceipt && leaderReceipt.execution_result === 'ERROR') {
        const errorMsg = leaderReceipt.genvm_result?.stderr || 'Contract execution error';
        throw new Error(errorMsg);
      }

      setTxStatus('Success! Legal defense guild established.');
      await fetchGuildsState();
      return receipt;
    } catch (err) {
      console.error('Guild creation failed:', err);
      setError(err.message || 'Transaction failed');
      setTxStatus('Failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Scan for Infringement (Submit evidence URL)
  const scanForInfringement = async (guildId, evidenceUrl) => {
    if (!glAccount || !CONTRACT_ADDRESS) {
      throw new Error('Wallet not connected');
    }
    setLoading(true);
    setError('');
    setTxHash('');
    setTxStatus(`Initiating copyright audit scan for guild #${guildId}...`);

    try {
      const client = getWriteClient(glAccount);
      const hash = await client.writeContract({
        address: CONTRACT_ADDRESS,
        functionName: 'scan_for_infringement',
        args: [Number(guildId), evidenceUrl.trim()],
      });
      
      setTxHash(hash);
      setTxStatus('GenLayer nodes are rendering the evidence URL and running AI IP legal audits. Please wait 15-30s...');

      const receipt = await client.waitForTransactionReceipt({ hash });
      
      const leaderReceipt = receipt.consensus_data?.leader_receipt?.[0];
      if (leaderReceipt && leaderReceipt.execution_result === 'ERROR') {
        const errorMsg = leaderReceipt.genvm_result?.stderr || 'Scan execution error';
        throw new Error(errorMsg);
      }

      setTxStatus('Consensus complete! AI Copyright analysis audit finalized.');
      await fetchGuildsState();
      return receipt;
    } catch (err) {
      console.error('Infringement scan failed:', err);
      setError(err.message || 'Transaction failed');
      setTxStatus('Failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (CONTRACT_ADDRESS && CONTRACT_ADDRESS !== '0x0000000000000000000000000000000000000000') {
      fetchGuildsState();
    }
  }, [CONTRACT_ADDRESS, address, fetchGuildsState]);

  return {
    address,
    guilds,
    contractBalance,
    loading,
    error,
    txHash,
    txStatus,
    connectWallet,
    fetchGuildsState,
    createGuild,
    scanForInfringement,
    contractAddress: CONTRACT_ADDRESS,
  };
}
