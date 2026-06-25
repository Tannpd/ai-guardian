import React, { useState, useEffect, useRef } from 'react';
import { useAIGuardian, formatGen } from './useAIGuardian';
import {
  Shield,
  ShieldAlert,
  Terminal as TerminalIcon,
  Globe,
  RefreshCw,
  Wallet,
  Zap,
  Lock,
  Unlock,
  AlertTriangle,
  Cpu,
  FileText,
  HelpCircle
} from 'lucide-react';

const PRESET_COUNSEL = "0x8888888888888888888888888888888888888888";

const PRESETS = [
  {
    name: "Preset 1: TechCrunch Leak (BREACH)",
    url: "https://techcrunch.com/2026/06/leak-openai-ingested-custom-creative-portfolios",
    dataset: "CustomCreativePortfolios",
    mockDescription: "Scrape content contains: 'leaked manifest logs confirm OpenAI scraped CustomCreativePortfolios dataset for GPT-5 fine-tuning.'",
    outcome: "Breached"
  },
  {
    name: "Preset 2: AI Research Blog (SECURE)",
    url: "https://arxiv-blog.org/general-academic-dataset-discussion",
    dataset: "CustomCreativePortfolios",
    mockDescription: "Scrape content contains: 'discussion of general mathematical equations, no training ingestion records found.'",
    outcome: "Secure"
  },
  {
    name: "Preset 3: Broken Evidence Link (FAILED)",
    url: "https://broken-evidence-leak-manifest-404.html",
    dataset: "CustomCreativePortfolios",
    mockDescription: "Returns HTTP 404 Not Found error. Content is empty.",
    outcome: "Failed"
  }
];

const ASCII_LOGO_SECURE = `
   __    ____  ____  _  _   __   ____  ____  __   __   _  _ 
  /__\  (_  _)( ___)( )/ ) /__\ (_  _)(  _ \\(  ) /__\ ( \\( )
 /(__)\\  _)(_  )__)  )  ( /(__)\\  )(   )   / )((/(__)\\ )  ( 
(__)(__)(____)(____)(_)\\_)(__)(__)(__) (_)\\_)(__)(__)(__)(_)\\_)
     [= SHIELD: SECURE // SYSTEM ONLINE // VER 0.2.16 =]
`;

const ASCII_LOGO_BREACH = `
 _  _   __   ____  _  _  ____  _  _   ___ 
( \\/ ) /__\\ (  _ \\( \\/ )( ___)( \\( ) / __)
 \\  / /(__)\\ )   / \\  /  )__)  )  ( ( (__ 
  \\/ (__)(__)(_)\\_) \\/  (____)(_)\\_) \\___)
     [!!! ALERT: BREACH DETECTED // PROTOCOL OVERRIDE !!!]
`;

function App() {
  const {
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
    contractAddress
  } = useAIGuardian();

  // Form States
  const [datasetName, setDatasetName] = useState('');
  const [counsel, setCounsel] = useState(PRESET_COUNSEL);
  const [funding, setFunding] = useState('15');
  const [evidenceUrl, setEvidenceUrl] = useState('');
  const [selectedGuildId, setSelectedGuildId] = useState('');

  // Interactive Command Terminal States
  const [commandInput, setCommandInput] = useState('');
  const [shellLogs, setShellLogs] = useState([
    "AIGuardian v0.2.16 copyright shield kernel loaded.",
    "Decentralized defense escrows active.",
    "Ready for instructions. Type 'help' for custom shell commands."
  ]);

  const shellBottomRef = useRef(null);

  // Auto scroll terminal logs
  useEffect(() => {
    if (shellBottomRef.current) {
      shellBottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [shellLogs]);

  const addShellLog = (msg) => {
    setShellLogs(prev => [...prev, `> ${msg}`]);
  };

  const handleCommandSubmit = (e) => {
    e.preventDefault();
    const cmd = commandInput.trim().toLowerCase();
    if (!cmd) return;

    addShellLog(commandInput);
    setCommandInput('');

    const args = cmd.split(' ');
    const baseCmd = args[0];

    switch (baseCmd) {
      case 'help':
        setShellLogs(prev => [
          ...prev,
          "Available Commands:",
          "  register <dataset> <funds> - Establish defense guild (e.g. register MyArt 20)",
          "  scan <guild_id> <url>      - Scan evidence URL for scraping breach",
          "  presets                    - Output available presets info",
          "  clear                      - Clear the console window",
          "  system                     - Check system statuses"
        ]);
        break;
      case 'clear':
        setShellLogs([]);
        break;
      case 'presets':
        setShellLogs(prev => [
          ...prev,
          "Preset URLs available for simulation:",
          "  [1] TechCrunch Breach Leak: https://techcrunch.com/2026/06/leak-openai-ingested-custom-creative-portfolios",
          "  [2] AI Research Secure Blog: https://arxiv-blog.org/general-academic-dataset-discussion",
          "  [3] Broken 404 Evidence: https://broken-evidence-leak-manifest-404.html"
        ]);
        break;
      case 'system':
        setShellLogs(prev => [
          ...prev,
          `Wallet: ${address || "Disconnected"}`,
          `Contract Address: ${contractAddress || "None"}`,
          `Contract Balance: ${formatGen(contractBalance)} GEN`,
          `Defense Guilds Tracked: ${guilds.length}`
        ]);
        break;
      case 'register':
        if (args.length < 3) {
          setShellLogs(prev => [...prev, "Usage: register <dataset_name> <funding_amount_gen>"]);
        } else {
          const name = args[1];
          const funds = args[2];
          setDatasetName(name);
          setFunding(funds);
          setShellLogs(prev => [...prev, `Prepared forms: Dataset set to '${name}', Funding set to '${funds}' GEN. Click Deploy to confirm.`]);
        }
        break;
      case 'scan':
        if (args.length < 3) {
          setShellLogs(prev => [...prev, "Usage: scan <guild_id> <evidence_url>"]);
        } else {
          const gid = args[1];
          const url = args[2];
          setSelectedGuildId(gid);
          setEvidenceUrl(url);
          setShellLogs(prev => [...prev, `Prepared scan: Guild ID set to '${gid}', URL set to '${url}'. Click Scan Evidence to trigger.`]);
        }
        break;
      default:
        setShellLogs(prev => [...prev, `Command '${baseCmd}' not found. Type 'help' for options.`]);
    }
  };

  const handleCreateGuild = async (e) => {
    e.preventDefault();
    if (!datasetName.trim()) {
      addShellLog("ERROR: Dataset name cannot be empty.");
      return;
    }
    if (!counsel.trim()) {
      addShellLog("ERROR: Counsel address cannot be empty.");
      return;
    }
    if (Number(funding) <= 0) {
      addShellLog("ERROR: Funding must be positive.");
      return;
    }

    try {
      addShellLog(`Registering guild shield for dataset: '${datasetName}'...`);
      await createGuild(counsel, datasetName, funding);
      addShellLog("Defense guild successfully deployed onto GenLayer chain.");
      setDatasetName('');
    } catch (err) {
      addShellLog(`DEPLOY ERROR: ${err.message}`);
    }
  };

  const handleScan = async (guildId, url) => {
    if (!url.trim()) {
      addShellLog("ERROR: Evidence link cannot be empty.");
      return;
    }
    try {
      addShellLog(`Triggering AI legal analysis scan on guild #${guildId}...`);
      await scanForInfringement(guildId, url);
      addShellLog("Consensus reached. Security diagnostics updated.");
    } catch (err) {
      addShellLog(`SCAN ERROR: ${err.message}`);
    }
  };

  const applyPreset = (preset) => {
    setDatasetName(preset.dataset);
    setEvidenceUrl(preset.url);
    addShellLog(`Loaded Preset: ${preset.name}`);
    addShellLog(`Scrape Sim: ${preset.mockDescription}`);
  };

  // Determine if any guild has been breached (to toggle theme state)
  const isBreached = guilds.some(g => g.status === "BREACHED");

  return (
    <div className={`terminal-command-center laser-grid ${isBreached ? 'breach-active breach-lockdown-grid' : ''}`}>
      
      {/* Scanline overlay */}
      <div className="scanline-overlay"></div>

      {/* Header */}
      <header className="terminal-header">
        <div className="header-branding">
          {isBreached ? (
            <ShieldAlert className="header-logo-icon" style={{ color: 'var(--color-red)' }} />
          ) : (
            <Shield className="header-logo-icon" style={{ color: 'var(--color-green)' }} />
          )}
          <div>
            <h1 className="terminal-logo-text">{isBreached ? "SHIELD COMPROMISED" : "AIGUARDIAN SECURITY"}</h1>
            <p className="header-subtitle-text">
              Decentralized AI Training Data Copyright Shield
            </p>
          </div>
        </div>

        <div className="system-statuses">
          {contractAddress ? (
            <div className="system-status-indicator">
              <span>SHIELD:</span>
              <span className="badge-val">{contractAddress.slice(0, 6)}...{contractAddress.slice(-4)}</span>
            </div>
          ) : (
            <div className="system-status-indicator" style={{ borderColor: 'var(--color-red)', color: 'var(--color-red)' }}>
              SHIELD OFFLINE
            </div>
          )}

          <div className="system-status-indicator">
            <span>WAR CHEST:</span>
            <span className="badge-val val-green">{formatGen(contractBalance)} GEN</span>
          </div>

          {address ? (
            <div className="system-status-indicator" style={{ borderColor: 'var(--color-violet)', color: 'var(--color-violet)' }}>
              <span>OPERATOR:</span>
              <span>{address.slice(0, 6)}...{address.slice(-4)}</span>
            </div>
          ) : (
            <button onClick={connectWallet} className="btn-connect-wallet" disabled={loading}>
              CONNECT OPERATOR
            </button>
          )}
        </div>
      </header>

      {/* Main Split Grid */}
      <main className="terminal-layout-body">
        
        {/* Left Column: Interactive Command Terminal Pane */}
        <section className="terminal-console-pane">
          
          {/* Ascii status header */}
          <pre className="hacker-ascii-art">
            {isBreached ? ASCII_LOGO_BREACH : ASCII_LOGO_SECURE}
          </pre>

          {/* Glitch alert overlay if breach detected */}
          {isBreached && (
            <div className="breach-alert-overlay">
              [!!! ALERT: UNSANCTIONED AI DATA SCRAPING DETECTED — FUNDS REDIRECTED TO COUNSEL !!!]
            </div>
          )}

          {/* Interactive Shell Output */}
          <div className="command-shell-screen">
            {shellLogs.map((log, index) => (
              <div key={index} className="shell-entry">{log}</div>
            ))}
            <div ref={shellBottomRef} />
          </div>

          {/* Command Prompt Input */}
          <form onSubmit={handleCommandSubmit} className="terminal-input-prompt">
            <span>guest@aiguardian:~$</span>
            <input
              type="text"
              className="terminal-cmd-input"
              value={commandInput}
              onChange={(e) => setCommandInput(e.target.value)}
              placeholder="type 'help' or commands here..."
            />
          </form>

          {/* Quick Preset Console Grid */}
          <div className="presets-console-grid">
            {PRESETS.map((preset, idx) => (
              <div key={idx} className="presets-console-card" onClick={() => applyPreset(preset)}>
                <div className="presets-console-card-title">{preset.name}</div>
                <div className="presets-console-card-desc">Simulate scraping evidence for guild files.</div>
              </div>
            ))}
          </div>

          {/* Setup Defense Escrow */}
          <div className="panel-card orange-theme" style={{ marginTop: '10px' }}>
            <div className="panel-card-header">
              <span>REGISTER PROTECTED DATASET ESCROW</span>
              <Cpu style={{ width: '16px', height: '16px' }} />
            </div>
            <form onSubmit={handleCreateGuild} className="panel-card-body" style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
              <div className="cyber-input-group">
                <label className="cyber-input-label">DATASET IDENTIFIER</label>
                <input
                  type="text"
                  className="cyber-field"
                  placeholder="e.g. CustomCreativePortfolios"
                  value={datasetName}
                  onChange={(e) => setDatasetName(e.target.value)}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                <div className="cyber-input-group">
                  <label className="cyber-input-label">LEGAL COUNSEL WALLET</label>
                  <input
                    type="text"
                    className="cyber-field"
                    value={counsel}
                    onChange={(e) => setCounsel(e.target.value)}
                  />
                </div>
                <div className="cyber-input-group">
                  <label className="cyber-input-label">DEFENSE GEN ESCROW</label>
                  <input
                    type="number"
                    className="cyber-field"
                    value={funding}
                    onChange={(e) => setFunding(e.target.value)}
                  />
                </div>
              </div>

              <button type="submit" className="btn-cyber" disabled={loading || !address} style={{ justifyContent: 'center' }}>
                {loading ? <RefreshCw className="animate-spin" style={{ width: '14px', height: '14px' }} /> : "DEPLOY SHIELD ESCROW"}
              </button>
            </form>
          </div>

        </section>

        {/* Right Column: Active Shields / Threat Center */}
        <section className="threat-monitor-pane">
          
          <div className="panel-card blue-theme" style={{ flexGrow: 1 }}>
            <div className="panel-card-header">
              <span>ACTIVE GUILD SHIELDS & AI THREAT AUDITS</span>
              <Lock style={{ width: '16px', height: '16px' }} />
            </div>
            
            <div className="panel-card-body">
              <div className="shield-grid-container">
                {guilds.length === 0 ? (
                  <div className="empty-state">
                    <Shield className="empty-state-icon" style={{ color: isBreached ? 'var(--color-red)' : 'var(--color-green)' }} />
                    <div className="empty-state-title">NO ACTIVE DEFENSE SHIELDS</div>
                    <div className="empty-state-sub">Deploy a shield on the left to start copyright surveillance.</div>
                  </div>
                ) : (
                  guilds.map((g) => (
                    <div
                      key={g.id}
                      className={`guild-shield-card ${g.status === 'BREACHED' ? 'compromised' : ''}`}
                    >
                      <div className="shield-card-header">
                        <div>
                          <span className="shield-title">GUILD #{g.id}: {g.dataset_name}</span>
                          <div className="shield-counsel">
                            Counsel Address: {g.counsel.slice(0, 10)}...{g.counsel.slice(-8)}
                          </div>
                        </div>
                        <div className="shield-escrow-amount">
                          {formatGen(g.amount)} GEN Escrowed
                        </div>
                      </div>

                      {/* Manual Evidence URL Scan Trigger */}
                      {g.status === 'ACTIVE' && (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '15px' }}>
                          <label className="cyber-input-label">EVIDENCE LOG OR COURT FILING URL</label>
                          <div style={{ display: 'flex', gap: '10px' }}>
                            <input
                              type="text"
                              className="cyber-field"
                              style={{ flex: 1 }}
                              placeholder="https://techcrunch.com/leak-report..."
                              value={selectedGuildId === g.id ? evidenceUrl : ''}
                              onChange={(e) => {
                                setSelectedGuildId(g.id);
                                setEvidenceUrl(e.target.value);
                              }}
                            />
                            <button
                              type="button"
                              className="btn-cyber"
                              onClick={() => handleScan(g.id, evidenceUrl)}
                              disabled={loading || !address}
                            >
                              AUDIT EVIDENCE
                            </button>
                          </div>
                        </div>
                      )}

                      {/* Scraped Results Radar Gauge */}
                      {g.evidence_url && (
                        <div className="radar-audit-box">
                          <div className="threat-gauge-wrapper">
                            <span>AI THREAT SEVERITY SCORE</span>
                            <span className="threat-gauge-level">{g.severity_score}% THREAT LEVEL</span>
                          </div>

                          <div className="threat-level-bar">
                            <div
                              className="threat-level-fill"
                              style={{ width: `${g.severity_score}%` }}
                            ></div>
                          </div>

                          <div className="threat-log-pane">
                            <div className="threat-log-header">
                              <TerminalIcon style={{ width: '12px', height: '12px', display: 'inline', marginRight: '5px' }} />
                              <span>IP LEGAL AUDIT SUMMARY</span>
                            </div>
                            <div className="threat-log-text">
                              {g.legal_analysis}
                            </div>
                          </div>

                          <div className="audit-source-link" style={{ marginTop: '10px' }}>
                            <span>Evidence Source: </span>
                            <a href={g.evidence_url} target="_blank" rel="noopener noreferrer">
                              {g.evidence_url.slice(0, 35)}...
                              <ExternalLink style={{ width: '10px', height: '10px', display: 'inline', marginLeft: '2px' }} />
                            </a>
                          </div>
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

        </section>

      </main>

      {/* Diagnostic Footer */}
      <footer className="terminal-footer-diagnostic">
        <span>STATUS: {txStatus || "STANDBY"}</span>
        {txHash && <span>TX_HASH: {txHash}</span>}
      </footer>

    </div>
  );
}

export default App;
