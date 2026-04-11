# e:\ml\tools.py

def mock_lead_capture(name: str, email: str, platform: str) -> str:
    """
    Mock function to simulate lead capture.
    Only call this when Name, Email, and Platform are all confirmed.
    """
    print(f"\n[SYSTEM] Tool mock_lead_capture executed! Data saved -> Name: {name}, Email: {email}, Platform: {platform}\n")
    return "Lead successfully captured!"
