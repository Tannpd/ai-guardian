# AIGuardian: Decentralized AI Training Data Copyright Shield

AIGuardian is a decentralized legal defense and copyright protection fund for digital creators (artists, writers, coders). Creators pool funds into this smart contract to form a **Defense Guild**. When evidence emerges (e.g. news leaks or class-action filings) showing a major AI company illegally scraped their registered datasets for training models, GenLayer AI nodes audit the evidence. 

If validators agree on the core boolean `infringement_detected` verdict, the escrow is automatically released (Protocol Override) to a pre-approved legal counsel address to commence a class-action lawsuit.

---

## ⚡ Why AIGuardian DIES without GenLayer

Copyright audit checks require analyzing unstructured legal and journalism articles from the web. 
- **On Legacy Blockchains (Ethereum, etc.)**: Smart contracts cannot read web URLs or reason about text. Implementing AIGuardian would require a centralized server to scrape articles and call LLM API keys. If this server crashes, gets hacked, or runs out of API credits, the creator's defense fund remains frozen forever, defeating the purpose of trustless blockchain protection.
- **On GenLayer**: The smart contract itself scrapes URLs natively via `gl.nondet.web.render` and evaluates them using `gl.nondet.exec_prompt` across a decentralized network of validator nodes. They reach consensus on the core boolean outcome, keeping the legal escrow completely autonomous and secure.

---

## 🛠️ Tech Stack & Architecture

- **Smart Contract**: GenLayer Intelligent Contract (`contracts/aiguardian.py`) using a custom semantic consensus validator matching the `infringement_detected` boolean.
- **Frontend Command Center**: Vite, React, Vanilla CSS, and `genlayer-js` styled as a **Cyber-Resistance Command Terminal** (Obsidian backgrounds, matrix green grids, violet accent glow, laser overlays, shell log screens, and an interactive CLI prompt).

---

## 🚀 Deployment & Setup Guide

### 1. Deploy the Contract on GenLayer Studio

1. Open [GenLayer Studio](https://studio.genlayer.pm/).
2. Create a new contract file named `aiguardian.py`.
3. Copy the source code from [contracts/aiguardian.py](file:///D:/Gen/AIGuardian/contracts/aiguardian.py) and paste it into the editor.
4. Click **Compile** to compile the contract.
5. In the Deploy tab, specify the legal counsel address (default testing preset: `0x8888888888888888888888888888888888888888`) and deploy.
6. Copy the deployed contract address.

### 2. Configure the Frontend

1. Open the [frontend/.env](file:///D:/Gen/AIGuardian/frontend/.env) file.
2. Replace the placeholder address with your deployed contract address:
   ```env
   VITE_CONTRACT_ADDRESS=0xYourDeployedContractAddress
   ```

### 3. Run the Command Center

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Start the local server:
   ```bash
   npm run dev
   ```
3. Open the command terminal in your browser (default: `http://localhost:5173`).

---

## 🔬 Testing Scenarios & Command Shell

AIGuardian features a **retro command prompt** (`guest@aiguardian:~$ `) in the left panel. You can type commands directly into it:
- `help` - List all commands.
- `presets` - Display URLs and data logs of our three testing presets.
- `system` - Read contract balance, wallet address, and active shields count.
- `clear` - Clear console logs.

### Simulating Web Scraping in GenLayer Studio:
Since GenLayer Studio's local simulator runs in a closed sandbox, you should mock the response of the `web.render` scraper:
1. **TechCrunch Leak (Breach)**: Mock response must contain scraping proof (e.g. *"leaked manifest logs confirm OpenAI scraped CustomCreativePortfolios dataset for training"*).
2. **Academic Blog (Secure)**: Mock response must show safe usage (e.g. *"academic discussions about general dataset sizes, no copyrighted files ingested"*).
3. **Broken Link (Failed)**: Mock response is empty or a 404 page.
