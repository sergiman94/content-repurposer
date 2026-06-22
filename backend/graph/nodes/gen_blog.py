"""Node 4a: Generate blog post."""

from backend.graph.nodes._llm_helpers import run_generation
from backend.graph.prompts.blog import BLOG_SYSTEM, BLOG_USER
from backend.graph.state import RepurposeState


def gen_blog(state: RepurposeState) -> dict:
    """Generate a 1000-1500 word SEO-optimized blog post.

    Reads: analysis, transcript
    Writes: blog_post, current_step, token_usage
    """
    return run_generation(
        state,
        system_prompt=BLOG_SYSTEM,
        user_prompt_template=BLOG_USER,
        step_name="gen_blog",
        output_key="blog_post",
    )
