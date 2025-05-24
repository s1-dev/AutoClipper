
class AI:
    BASE_YT_DETAIL_PROMPT = f"""
        Generate an SEO-optimized title, description, and tag list for the following transcript.
        Please ensure the title is no longer than 100 chars, the description is no longer than 5000 chars, and the tags list
        is no longer than 500 chars.
        Please return the response as a JSON object with the following keys: "videoTitle", "videoDesc", and "videoTags". The "tags" value should be a list of strings.
    """

class CLI:
    TITLE_LINE = "~~~~~~~~~~~~~~~~~~~~~~~~"
    CONFIG_SEPERATOR = "------------------------"
