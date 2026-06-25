# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

# =============================================================================
#  aiguardian.py — AIGuardian: AI Copyright Infringement Escrow Contract
#  GenLayer Intelligent Contract (v0.2.16)
# =============================================================================

from genlayer import *
import json

class Contract(gl.Contract):
    """
    AIGuardian — Decentralized AI Training Data Copyright Shield
    ============================================================
    A decentralized legal defense and copyright protection fund for digital creators. 
    Creators pool funds into this smart contract to form a "Defense Guild". 
    If evidence emerges (e.g. court filings or leaked manifests) showing a tech company 
    illegally scraped their data for AI training, GenLayer AI nodes scrape the page 
    and perform an IP legal audit. 
    
    If nodes agree on the core boolean `infringement_detected` verdict, consensus is reached. 
    If true, the locked funds are automatically released to a pre-approved legal counsel 
    address to commence litigation.
    """

    # Monotonic guild counter
    guilds_count:                 u64

    # Storage Mappings (Pre-initialized by VM)
    guild_creator:                TreeMap[u64, Address]
    guild_counsel:                TreeMap[u64, Address]
    guild_amount:                 TreeMap[u64, u256]
    guild_dataset_name:           TreeMap[u64, str]
    guild_evidence_url:           TreeMap[u64, str]
    guild_status:                 TreeMap[u64, str]       # "ACTIVE", "BREACHED", "FAILED"
    guild_infringement_detected:  TreeMap[u64, bool]
    guild_severity_score:         TreeMap[u64, u256]      # Sized integer to avoid compilation errors
    guild_legal_analysis:         TreeMap[u64, str]

    # ═══════════════════════════════════════════════════════════════════
    # CONSTRUCTOR
    # ═══════════════════════════════════════════════════════════════════
    def __init__(self) -> None:
        self.guilds_count = 0

    # ═══════════════════════════════════════════════════════════════════
    # PUBLIC WRITE: CREATE GUILD & LOCK DEFENSE FUND
    # ═══════════════════════════════════════════════════════════════════
    @gl.public.write
    def create_guild(self, counsel: Address, dataset_name: str) -> int:
        """
        Register a protected dataset and deposit GEN tokens into the legal defense escrow.
        """
        amount = int(gl.message.value)
        if amount <= 0:
            raise UserError("Guild defense fund deposit must be greater than zero.")

        if len(dataset_name.strip()) == 0:
            raise UserError("Protected dataset name cannot be empty.")

        if str(counsel) == "0x0000000000000000000000000000000000000000":
            raise UserError("Invalid legal counsel address.")

        gid = self.guilds_count

        self.guild_creator[gid] = gl.message.sender_address
        self.guild_counsel[gid] = counsel
        self.guild_amount[gid] = amount
        self.guild_dataset_name[gid] = dataset_name.strip()
        self.guild_evidence_url[gid] = ""
        self.guild_status[gid] = "ACTIVE"
        self.guild_infringement_detected[gid] = False
        self.guild_severity_score[gid] = 0
        self.guild_legal_analysis[gid] = "Defense fund secured. Monitoring AI scraping activities and public evidence logs..."

        self.guilds_count = int(gid) + 1
        return int(gid)

    # ═══════════════════════════════════════════════════════════════════
    # PUBLIC WRITE: SCAN & AUDIT FOR INFRINGEMENT
    # ═══════════════════════════════════════════════════════════════════
    @gl.public.write
    def scan_for_infringement(self, guild_id: int, evidence_url: str) -> None:
        """
        Scrapes and audits submitted evidence. Releases the legal defense fund to counsel
        if AI copyright infringement is verified by consensus.
        """
        if guild_id < 0 or guild_id >= int(self.guilds_count):
            raise UserError("Guild does not exist.")

        status = self.guild_status.get(guild_id, "ACTIVE")
        if status != "ACTIVE" and status != "FAILED":
            raise UserError("Guild is not in active or failed state.")

        amount = int(self.guild_amount.get(guild_id, 0))
        if amount <= 0:
            raise UserError("Guild escrow has no locked funds.")

        dataset_name = self.guild_dataset_name.get(guild_id, "")
        counsel = self.guild_counsel.get(guild_id, Address("0x0000000000000000000000000000000000000000"))

        if len(evidence_url.strip()) == 0:
            raise UserError("Evidence URL cannot be empty.")

        url_lower = evidence_url.lower().strip()
        if not (url_lower.startswith("http://") or url_lower.startswith("https://")):
            raise UserError("Invalid URL format. Must start with http:// or https://")

        self.guild_evidence_url[guild_id] = evidence_url.strip()
        self.guild_status[guild_id] = "ACTIVE"
        self.guild_legal_analysis[guild_id] = "IP Legal & Cybersecurity Analyst is processing submitted evidence..."

        # ── Non-Deterministic Execution block ───────────────────────────
        def leader_fn() -> str:
            # 1. Scrape evidence page
            try:
                evidence_raw = gl.nondet.web.render(evidence_url)
                evidence_text = evidence_raw.strip()
            except Exception as e:
                return json.dumps({
                    "error": "EVIDENCE_SCRAPE_FAILED",
                    "infringement_detected": False,
                    "severity_score": 0,
                    "legal_analysis": f"Failed to retrieve or render the evidence URL: {str(e)}"
                })

            if len(evidence_text) < 15:
                return json.dumps({
                    "error": "EMPTY_EVIDENCE",
                    "infringement_detected": False,
                    "severity_score": 0,
                    "legal_analysis": "The evidence page appeared to be empty or unparseable. Cannot verify infringement claims."
                })

            evidence_excerpt = evidence_text[:4000]

            # 2. AI IP Legal Analyst prompt
            prompt = f"""You are an "IP Legal & Cybersecurity Analyst" specializing in AI copyright law, data mining licenses, and digital rights management.
Your job is to read the submitted evidence and determine if the guild's dataset has been scraped or used without authorization to train commercial AI models.

Protected Dataset Name:
"{dataset_name}"

Submitted Evidence Document Text:
--- START EVIDENCE TEXT ---
{evidence_excerpt}
--- END EVIDENCE TEXT ---

Please analyze the document under these guidelines:
1. Examine if the text contains proof or substantial allegations that the dataset "{dataset_name}" was scraped, index-mined, leaked, or included in an AI training set (e.g. OpenAI, Midjourney, Stability AI).
2. Look for specific technical mentions of the dataset name or matching artist portfolios being processed or utilized.
3. Determine "infringement_detected" (true or false). Set it to true ONLY if the text contains clear evidence, audits, or legal claims indicating unauthorized data mining or ingestion of the specific dataset "{dataset_name}". Set to false if the evidence is generic, rumors, unrelated to this dataset, or disproven.
4. Calculate a "severity_score" (integer from 0 to 100) representing the severity of data theft and impact.
5. Summarize your findings in 2-3 concise sentences as the "legal_analysis", outlining the scraping evidence or lack thereof.

Your output MUST be a valid JSON object with EXACTLY the following keys:
{{
  "infringement_detected": true | false,
  "severity_score": <0-100>,
  "legal_analysis": "<2-3 sentences summarizing the legal finding, naming the violating company if applicable>"
}}
Do NOT wrap the JSON in markdown code blocks. Do NOT add any extra text. Return ONLY the raw JSON."""

            try:
                raw_output = gl.nondet.exec_prompt(prompt)
            except Exception as e:
                return json.dumps({
                    "error": f"LLM_EXECUTION_FAILED: {str(e)}",
                    "infringement_detected": False,
                    "severity_score": 0,
                    "legal_analysis": "AI node failed to execute IP copyright evaluation."
                })

            cleaned = raw_output.strip()
            if cleaned.startswith("```"):
                lines = cleaned.split("\n")
                inner = []
                for line in lines[1:]:
                    if line.strip() == "```":
                        break
                    inner.append(line)
                cleaned = "\n".join(inner).strip()

            try:
                parsed = json.loads(cleaned)
                is_infringed = bool(parsed.get("infringement_detected", False))
                severity = int(parsed.get("severity_score", 0))
                if severity < 0:
                    severity = 0
                elif severity > 100:
                    severity = 100
                analysis_str = str(parsed.get("legal_analysis", "No legal summary provided.")).strip()

                return json.dumps({
                    "infringement_detected": is_infringed,
                    "severity_score": severity,
                    "legal_analysis": analysis_str[:1000]
                })
            except Exception as e:
                return json.dumps({
                    "error": f"JSON_PARSE_FAILED: {str(e)}",
                    "infringement_detected": False,
                    "severity_score": 0,
                    "legal_analysis": f"AI response was not valid JSON: {cleaned}"
                })

        def validator_fn(leader_result: str) -> bool:
            """
            Semantic Validator: Core Boolean Consensus on 'infringement_detected'.
            Different nodes might generate slightly different summaries or severity scores.
            Consensus is reached as long as all validator nodes agree on the boolean outcome.
            """
            try:
                leader_data = json.loads(leader_result)
            except Exception:
                return False

            if "error" in leader_data:
                allowed_errors = {"EVIDENCE_SCRAPE_FAILED", "EMPTY_EVIDENCE", "LLM_EXECUTION_FAILED", "JSON_PARSE_FAILED"}
                return any(err in str(leader_data.get("error", "")) for err in allowed_errors)

            validator_raw = leader_fn()
            try:
                validator_data = json.loads(validator_raw)
            except Exception:
                return True  # Abstain on local error

            if "error" in validator_data:
                return True

            leader_detected = bool(leader_data.get("infringement_detected", False))
            validator_detected = bool(validator_data.get("infringement_detected", False))

            return leader_detected == validator_detected

        # Run non-deterministic consensus
        consensus_json = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)

        try:
            res = json.loads(consensus_json)
        except Exception:
            self.guild_status[guild_id] = "FAILED"
            self.guild_legal_analysis[guild_id] = "Consensus outcome was unparseable."
            return

        if "error" in res:
            self.guild_status[guild_id] = "FAILED"
            self.guild_legal_analysis[guild_id] = f"Audit failed: {res.get('error')}. Info: {res.get('legal_analysis')}"
            return

        is_infringed = bool(res.get("infringement_detected", False))
        severity = int(res.get("severity_score", 0))
        analysis_str = str(res.get("legal_analysis", "AI copyright audit completed."))

        self.guild_infringement_detected[guild_id] = is_infringed
        self.guild_severity_score[guild_id] = severity
        self.guild_legal_analysis[guild_id] = analysis_str

        if is_infringed:
            # Copyright infringement verified! Release legal funds to counsel
            self.guild_amount[guild_id] = 0
            self.guild_status[guild_id] = "BREACHED"

            counsel_contract = gl.get_contract_at(counsel)
            counsel_contract.emit_transfer(value=u256(amount))
        else:
            # No infringement detected, fund remains active
            self.guild_status[guild_id] = "ACTIVE"

    # ═══════════════════════════════════════════════════════════════════
    # READ-ONLY VIEW METHODS
    # ═══════════════════════════════════════════════════════════════════
    @gl.public.view
    def get_guild(self, guild_id: int) -> str:
        """
        Returns JSON details of a specific guild.
        """
        if guild_id < 0 or guild_id >= int(self.guilds_count):
            return "{}"

        creator = self.guild_creator.get(guild_id, Address("0x0000000000000000000000000000000000000000"))
        counsel = self.guild_counsel.get(guild_id, Address("0x0000000000000000000000000000000000000000"))
        amount = int(self.guild_amount.get(guild_id, 0))
        dataset = self.guild_dataset_name.get(guild_id, "")
        evidence = self.guild_evidence_url.get(guild_id, "")
        status = self.guild_status.get(guild_id, "ACTIVE")
        detected = bool(self.guild_infringement_detected.get(guild_id, False))
        severity = int(self.guild_severity_score.get(guild_id, 0))
        analysis = self.guild_legal_analysis.get(guild_id, "")

        return json.dumps({
            "id": guild_id,
            "creator": str(creator),
            "counsel": str(counsel),
            "amount": amount,
            "dataset_name": dataset,
            "evidence_url": evidence,
            "status": status,
            "infringement_detected": detected,
            "severity_score": severity,
            "legal_analysis": analysis
        })

    @gl.public.view
    def get_guilds_count(self) -> int:
        return int(self.guilds_count)
