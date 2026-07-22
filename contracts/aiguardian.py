# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

# =============================================================================
#  aiguardian.py - AIGuardian: AI Copyright Infringement Escrow Contract
#  GenLayer Intelligent Contract (v0.2.16)
# =============================================================================

from genlayer import *
import json

class UserError(Exception):
    pass

def to_address(val) -> Address:
    """
    Ensures input addresses are represented as pure Address structures,
    protecting against string/int input deserialization issues in GenLayer Studio UI.
    """
    if isinstance(val, Address):
        return val
    if isinstance(val, int):
        return Address(f"0x{val:040x}")
    if isinstance(val, str):
        if val.startswith("0x"):
            return Address(val)
        try:
            return Address(f"0x{int(val):040x}")
        except Exception:
            return Address(val)
    return Address(str(val))

class Contract(gl.Contract):
    """
    AIGuardian - Decentralized AI Training Data Copyright Shield
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
    guilds_count:                 bigint

    # Storage Mappings (Pre-initialized by VM)
    guild_creator:                TreeMap[str, Address]
    guild_counsel:                TreeMap[str, Address]
    guild_amount:                 TreeMap[str, bigint]
    guild_dataset_name:           TreeMap[str, str]
    guild_evidence_url:           TreeMap[str, str]
    guild_status:                 TreeMap[str, str]       # "ACTIVE", "BREACHED", "FAILED"
    guild_infringement_detected:  TreeMap[str, bool]
    guild_severity_score:         TreeMap[str, bigint]
    guild_legal_analysis:         TreeMap[str, str]

    # CONSTRUCTOR
    def __init__(self) -> None:
        self.guilds_count = bigint(0)

    # PUBLIC WRITE: CREATE GUILD & LOCK DEFENSE FUND
    @gl.public.write.payable
    def create_guild(self, counsel: Address, dataset_name: str) -> int:
        """
        Register a protected dataset and deposit GEN tokens into the legal defense escrow.
        """
        amount = gl.message.value
        if amount <= bigint(0):
            raise UserError("Guild defense fund deposit must be greater than zero.")

        if len(dataset_name.strip()) == 0:
            raise UserError("Protected dataset name cannot be empty.")

        counsel_clean = to_address(counsel)
        if str(counsel_clean) == "0x0000000000000000000000000000000000000000":
            raise UserError("Invalid legal counsel address.")

        gid = self.guilds_count
        gid_str = str(gid)
        sender = to_address(gl.message.sender_address)

        self.guild_creator[gid_str] = sender
        self.guild_counsel[gid_str] = counsel_clean
        self.guild_amount[gid_str] = amount
        self.guild_dataset_name[gid_str] = dataset_name.strip()
        self.guild_evidence_url[gid_str] = ""
        self.guild_status[gid_str] = "ACTIVE"
        self.guild_infringement_detected[gid_str] = False
        self.guild_severity_score[gid_str] = bigint(0)
        self.guild_legal_analysis[gid_str] = "Defense fund secured. Monitoring AI scraping activities and public evidence logs..."

        self.guilds_count = gid + bigint(1)
        return int(gid)

    # PUBLIC WRITE: SCAN & AUDIT FOR INFRINGEMENT
    @gl.public.write
    def scan_for_infringement(self, guild_id: int, evidence_url: str) -> None:
        """
        Scrapes and audits submitted evidence. Releases the legal defense fund to counsel
        if AI copyright infringement is verified by consensus.
        """
        gid_str = str(guild_id)
        if guild_id < 0 or bigint(guild_id) >= self.guilds_count:
            raise UserError("Guild does not exist.")

        # Access Control: Restrict trigger to authenticated guild participants
        sender = to_address(gl.message.sender_address)
        creator = to_address(self.guild_creator.get(gid_str, Address("0x0000000000000000000000000000000000000000")))
        counsel = to_address(self.guild_counsel.get(gid_str, Address("0x0000000000000000000000000000000000000000")))

        if str(sender) != str(creator) and str(sender) != str(counsel):
            raise UserError("Only the guild creator or legal counsel can trigger a copyright audit.")

        status = self.guild_status.get(gid_str, "ACTIVE")
        if status != "ACTIVE" and status != "FAILED":
            raise UserError("Guild is not in active or failed state.")

        amount = self.guild_amount.get(gid_str, bigint(0))
        if amount <= bigint(0):
            raise UserError("Guild escrow has no locked funds.")

        dataset_name = self.guild_dataset_name.get(gid_str, "")

        if len(evidence_url.strip()) == 0:
            raise UserError("Evidence URL cannot be empty.")

        url_lower = evidence_url.lower().strip()
        if not (url_lower.startswith("http://") or url_lower.startswith("https://")):
            raise UserError("Invalid URL format. Must start with http:// or https://")

        self.guild_evidence_url[gid_str] = evidence_url.strip()
        self.guild_status[gid_str] = "ACTIVE"
        self.guild_legal_analysis[gid_str] = "IP Legal & Cybersecurity Analyst is processing submitted evidence..."

        # Non-Deterministic Execution block
        def leader_fn() -> str:
            # 1. Scrape evidence page
            try:
                evidence_raw = gl.nondet.web.render(evidence_url)
                if isinstance(evidence_raw, bytes):
                    evidence_text = evidence_raw.decode('utf-8', errors='ignore').strip()
                else:
                    evidence_text = str(evidence_raw).strip()
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
            prompt = f"""You are an IP Legal & Cybersecurity Analyst specializing in AI copyright law, data mining licenses, and digital rights management.
Your job is to read the submitted evidence and determine if the guild's dataset has been scraped or used without authorization to train commercial AI models.

Protected Dataset Name:
"{dataset_name}"

Submitted Evidence Document Text:
--- START EVIDENCE TEXT ---
{evidence_excerpt}
--- END EVIDENCE TEXT ---

Please analyze the document under these guidelines:
1. Examine if the text contains proof or substantial allegations that the dataset "{dataset_name}" was scraped, index-mined, leaked, or included in an AI training set.
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
                if isinstance(raw_output, bytes):
                    raw_str = raw_output.decode('utf-8', errors='ignore').strip()
                else:
                    raw_str = str(raw_output).strip()
            except Exception as e:
                return json.dumps({
                    "error": f"LLM_EXECUTION_FAILED: {str(e)}",
                    "infringement_detected": False,
                    "severity_score": 0,
                    "legal_analysis": "AI node failed to execute IP copyright evaluation."
                })

            cleaned = raw_str.strip()
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
            Returns False on local scrape or parsing errors to fail closed.
            """
            try:
                if isinstance(leader_result, bytes):
                    leader_str = leader_result.decode('utf-8', errors='ignore')
                else:
                    leader_str = str(leader_result)
                l_start = leader_str.find('{')
                l_end = leader_str.rfind('}')
                if l_start == -1 or l_end == -1 or l_start > l_end:
                    return False
                cleaned_leader = leader_str[l_start:l_end+1]
                leader_data = json.loads(cleaned_leader)
            except Exception:
                return False

            if "error" in leader_data:
                return False

            validator_raw = leader_fn()
            try:
                if isinstance(validator_raw, bytes):
                    val_str = validator_raw.decode('utf-8', errors='ignore')
                else:
                    val_str = str(validator_raw)
                v_start = val_str.find('{')
                v_end = val_str.rfind('}')
                if v_start == -1 or v_end == -1 or v_start > v_end:
                    return False
                cleaned_val = val_str[v_start:v_end+1]
                validator_data = json.loads(cleaned_val)
            except Exception:
                return False

            if "error" in validator_data:
                return False

            leader_detected = bool(leader_data.get("infringement_detected", False))
            validator_detected = bool(validator_data.get("infringement_detected", False))

            return leader_detected == validator_detected

        # Run non-deterministic consensus
        consensus_json = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)

        try:
            if isinstance(consensus_json, bytes):
                cons_str = consensus_json.decode('utf-8', errors='ignore')
            else:
                cons_str = str(consensus_json)
            cons_start = cons_str.find('{')
            cons_end = cons_str.rfind('}')
            if cons_start == -1 or cons_end == -1 or cons_start > cons_end:
                raise ValueError("No JSON object found")
            cleaned_cons = cons_str[cons_start:cons_end+1]
            res = json.loads(cleaned_cons)
        except Exception:
            self.guild_status[gid_str] = "FAILED"
            self.guild_legal_analysis[gid_str] = "Consensus outcome was unparseable."
            return

        if "error" in res:
            self.guild_status[gid_str] = "FAILED"
            self.guild_legal_analysis[gid_str] = f"Audit failed: {res.get('error')}. Info: {res.get('legal_analysis')}"
            return

        is_infringed = bool(res.get("infringement_detected", False))
        severity = int(res.get("severity_score", 0))
        analysis_str = str(res.get("legal_analysis", "AI copyright audit completed."))

        self.guild_infringement_detected[gid_str] = is_infringed
        self.guild_severity_score[gid_str] = bigint(severity)
        self.guild_legal_analysis[gid_str] = analysis_str

        if is_infringed:
            # Copyright infringement verified! Release legal funds to counsel
            self.guild_amount[gid_str] = bigint(0)
            self.guild_status[gid_str] = "BREACHED"

            counsel_addr = to_address(counsel)
            counsel_contract = gl.get_contract_at(counsel_addr)
            try:
                counsel_contract.emit_transfer(value=bigint(amount))
            except Exception:
                pass
        else:
            # No infringement detected, fund remains active
            self.guild_status[gid_str] = "ACTIVE"

    # READ-ONLY VIEW METHODS
    @gl.public.view
    def get_guild(self, guild_id: int) -> str:
        """
        Returns JSON details of a specific guild.
        """
        gid_str = str(guild_id)
        if guild_id < 0 or bigint(guild_id) >= self.guilds_count:
            return "{}"

        creator = self.guild_creator.get(gid_str, Address("0x0000000000000000000000000000000000000000"))
        counsel = self.guild_counsel.get(gid_str, Address("0x0000000000000000000000000000000000000000"))
        amount = self.guild_amount.get(gid_str, bigint(0))
        dataset = self.guild_dataset_name.get(gid_str, "")
        evidence = self.guild_evidence_url.get(gid_str, "")
        status = self.guild_status.get(gid_str, "ACTIVE")
        detected = bool(self.guild_infringement_detected.get(gid_str, False))
        severity = int(self.guild_severity_score.get(gid_str, bigint(0)))
        analysis = self.guild_legal_analysis.get(gid_str, "")

        return json.dumps({
            "id": guild_id,
            "creator": str(creator),
            "counsel": str(counsel),
            "amount": int(amount),
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
