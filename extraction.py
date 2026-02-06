import re

def extract_business_card_details(text):
    """
    Block-Centric Extraction: Groups lines into functional zones (Identity, Address, Contact)
    to achieve maximum accuracy.
    """
    details = {
        "Name": "Not Found",
        "Job Title": "Not Found",
        "Company": "Not Found",
        "Email": "Not Found",
        "Phone": "Not Found",
        "Address": "Not Found",
        "Website": "Not Found"
    }

    raw_lines = [line.strip() for line in text.split('\n') if line.strip()]
    if not raw_lines:
        return details

    used_indices = set()
    
    # regex patterns
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    url_pattern = r'(?:https?:\/\/|www\.)[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:\/[^\s]*)?'
    phone_pattern = r'(?:(?:\+|00)[\s.-]{0,3})?(?:\d[\s.-]{0,3}){7,15}'
    
    # ---------------- 1. ANCHOR FIELDS (CONTACT BLOCK) ----------------
    for idx, line in enumerate(raw_lines):
        line_l = line.lower()
        # Email
        email_match = re.search(email_pattern, line)
        if email_match:
            if details["Email"] == "Not Found":
                details["Email"] = email_match.group()
            if len(line.replace(email_match.group(), "").strip()) < 5:
                used_indices.add(idx)

        # Website
        url_match = re.search(url_pattern, line)
        if url_match:
             if details["Website"] == "Not Found":
                 details["Website"] = url_match.group()
             if len(line.replace(url_match.group(), "").strip()) < 5:
                 used_indices.add(idx)
        
        # Phone (Aggressive with extensions)
        phone_patterns = [
            r'(?:(?:\+|00)[\s.-]{0,3})?(?:\d[\s.-]{0,3}){8,15}(?:\s*/\s*\d{2,4})?', # With optional / EXT
            r'\(\d{3,5}\)\s*\d{6,8}(?:\s*/\s*\d{2,4})?', # Area code with optional / EXT
            r'\b\d{10}\b'
        ]
        is_phone_line = False
        # Use word boundaries for phone keywords to avoid matching "Telangana" as "tel"
        if any(re.search(r'\b' + kw + r'\b', line_l) for kw in ["tel", "phone", "mobile", "cell", "fax"]):
            is_phone_line = True
        elif ":" in line:
            # If line has a colon and digits, it's likely a contact field
            if re.search(r'\d', line):
                is_phone_line = True
        
        for p in phone_patterns:
            match = re.search(p, line)
            if match:
                digits = re.sub(r'\D', '', match.group())
                if len(digits) >= 8:
                    if details["Phone"] == "Not Found":
                        details["Phone"] = match.group().strip()
                    elif match.group().strip() not in details["Phone"]:
                        details["Phone"] += f", {match.group().strip()}"
                    is_phone_line = True
        
        if is_phone_line:
            used_indices.add(idx)

    # ---------------- 2. TAGGING & BLOCKS ----------------
    address_keywords = [
        "st.", "road", "rd.", "ave", "lane", "suite", "floor", "block", "sector", "hwy", "bldg", "plot", "h.no",
        "industrial", "phase", "mandal", "taluka", "village", "dist", "district", "pincode", "pin code", 
        "opposite", "near", "beside", "tower", "garden", "park", "square", "colony", "nagar", "enclave", "boulevard", 
        "plaza", "terrace", "po box", "postal", "zip", "apt", "unit", "level", "ida", "industrial estate"
    ]
    
    regions = [
        "Andhra", "Assam", "Bihar", "Gujarat", "Haryana", "Karnataka", "Kerala", "Maharashtra", "Punjab", 
        "Rajasthan", "Tamil Nadu", "Telangana", "Uttar", "Bengal", "Delhi", "California", "New York", "Texas", 
        "Province", "County", "Region", "State"
    ]

    job_keywords = ["Manager", "Director", "Chief", "Lead", "Head", "Consultant", "Engineer", "Developer", "Designer", "Sales", "Executive", "CEO", "CTO", "Founder", "President"]
    company_suffixes = ["inc", "ltd", "llc", "corp", "limited", "pvt ltd", "private limited", "group", "solutions", "global", "systems", "technologies", "company", "gmbh", "ag", "plc", "s.r.l."]

    line_tags = []
    for idx, line in enumerate(raw_lines):
        if idx in used_indices: 
            line_tags.append("Used")
            continue
        
        line_l = line.lower()
        tag = "Generic"
        
        # Priority 1: Company Suffix
        if any(re.search(r'\b' + re.escape(s) + r'\b', line_l) for s in company_suffixes):
            tag = "Company"
        # Priority 2: Job Title
        elif any(kw in line for kw in job_keywords):
            tag = "Job"
        # Priority 3: Address Triggers
        else:
            has_postal = re.search(r'\b\d{5,6}\b', line) or re.search(r'\b[A-Z]{1,2}\d[A-Z\d]? \d[A-Z]{2}\b', line, re.I)
            if any(kw in line_l for kw in address_keywords) or any(r.lower() in line_l for r in regions) or has_postal:
                tag = "Address"
            elif line[0].isupper() and len(line) > 3 and not any(char.isdigit() for char in line):
                tag = "Identity"
            
        line_tags.append(tag)

    # ---------------- 3. ADDRESS ZONE (SPATIAL CLUSTERING) ----------------
    # Find all potential address parts (Address tagged or Generic between triggers)
    addr_indices = [i for i, t in enumerate(line_tags) if t == "Address"]
    
    if addr_indices:
        # Start with the first address trigger and expand to capture the vertical block
        # We find the biggest trigger block
        groups = []
        if addr_indices:
            curr = [addr_indices[0]]
            for i in range(1, len(addr_indices)):
                if addr_indices[i] <= curr[-1] + 3: # Allow larger vertical gaps
                    curr.append(addr_indices[i])
                else:
                    groups.append(curr)
                    curr = [addr_indices[i]]
            groups.append(curr)
        
        best_block = list(max(groups, key=len))
        
        # Expand block to catch prefix lines (like Company or redundant name)
        # but STOP at obvious field changes (Job, Identity)
        while best_block[0] > 0:
            prev = best_block[0] - 1
            if prev in used_indices or line_tags[prev] in ["Job", "Identity"]: break
            best_block.insert(0, prev)
            
        while best_block[-1] < len(raw_lines) - 1:
            nxt = best_block[-1] + 1
            if nxt in used_indices or line_tags[nxt] in ["Job", "Identity"]: break
            best_block.append(nxt)

        final_addr_parts = []
        for b_idx in best_block:
            if b_idx not in used_indices:
                # Clean up punctuation before joining to avoid double commas
                p = raw_lines[b_idx].rstrip(',. ')
                final_addr_parts.append(p)
                # Note: We mark as used, but we let Company extraction run separately if needed
                used_indices.add(b_idx)
        details["Address"] = ", ".join(final_addr_parts)

    # ---------------- 4. IDENTITY ZONE (NAME & JOB) ----------------
    # Job Title first
    job_idx = -1
    for idx, tag in enumerate(line_tags):
        if tag == "Job" and idx not in used_indices:
            details["Job Title"] = raw_lines[idx]
            job_idx = idx
            used_indices.add(idx)
            break
            
    # Name (closest to Job)
    name_candidates = []
    for idx, tag in enumerate(line_tags):
        if idx in used_indices: continue
        if tag in ["Identity", "Generic"] and len(raw_lines[idx]) > 3:
            # Sophisticated logo cleaning
            cleaned = re.sub(r'\s+[A-Z]{1,4}(\s+[A-Za-z]{2,4})?$', '', raw_lines[idx]).strip()
            name_candidates.append((idx, cleaned))

    if name_candidates:
        if job_idx != -1:
            best_name = min(name_candidates, key=lambda x: abs(x[0] - job_idx))
            details["Name"] = best_name[1]
            used_indices.add(best_name[0])
        else:
            details["Name"] = name_candidates[0][1]
            used_indices.add(name_candidates[0][0])

    # ---------------- 5. COMPANY ----------------
    # Re-check ALL lines for company suffixes to ensure we get the best main Company line
    # Even if used in address, we want it as the 'Company' field if it's the strongest match
    best_company = "Not Found"
    for idx, line in enumerate(raw_lines):
        if any(re.search(r'\b' + re.escape(s) + r'\b', line.lower()) for s in company_suffixes):
            # Prioritize all-caps or long matches
            if best_company == "Not Found" or len(line) > len(best_company):
                best_company = line

    if best_company != "Not Found":
        details["Company"] = best_company

    if details["Company"] == "Not Found" and details["Email"] != "Not Found":
        domain = details["Email"].split("@")[-1].split(".")[0]
        if domain not in ["gmail", "yahoo", "hotmail", "outlook"]:
            details["Company"] = domain.capitalize()

    return details
