import os


def get_clip_path(folder, title, extension):
    """Get a path for a clip by folder and title."""
    return f"~/pornhub/{folder}/{title}.{extension}"


def symlink_duplicate(clip, new_path):
    """Handle multiple references to a clip

    If a clip has already been downloaded, but is used in another source as well,
    symlink the existing file to the new location.
    """
    # Handle legacy clips (pre "location" migration)
    if clip.location is None:
        return

    # Same location, nothing to do here
    if clip.location == new_path:
        return

    os.link(clip.location, new_path)
