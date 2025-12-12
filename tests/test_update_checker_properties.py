"""
Property-based tests for update checker.

These tests use Hypothesis to verify correctness properties across many random inputs.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume

from update.update_checker import UpdateChecker
from update.models import UpdateInfo


# Strategy for generating valid version components
version_component = st.integers(min_value=0, max_value=999)

# Strategy for generating valid version tuples
version_tuple = st.tuples(version_component, version_component, version_component)


def version_tuple_to_string(v: tuple, with_prefix: bool = False) -> str:
    """Convert a version tuple to a string."""
    version_str = f"{v[0]}.{v[1]}.{v[2]}"
    if with_prefix:
        return f"v{version_str}"
    return version_str


# Strategy for generating valid GitHub API responses
@st.composite
def github_release_response(draw):
    """Generate a valid GitHub release API response."""
    version = draw(version_tuple)
    version_str = version_tuple_to_string(version, with_prefix=draw(st.booleans()))
    
    release_notes = draw(st.text(min_size=0, max_size=500, alphabet=st.characters(
        whitelist_categories=('L', 'N', 'P', 'Z'),
        whitelist_characters='\n'
    )))
    
    file_size = draw(st.integers(min_value=1000, max_value=100_000_000))
    
    exe_name = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('L', 'N'),
    ))) + ".exe"
    
    download_url = f"https://github.com/owner/repo/releases/download/{version_str}/{exe_name}"
    
    published_at = draw(st.datetimes()).isoformat() + "Z"
    
    return {
        "tag_name": version_str,
        "name": f"Version {version_str}",
        "body": release_notes,
        "published_at": published_at,
        "assets": [
            {
                "name": exe_name,
                "size": file_size,
                "browser_download_url": download_url
            }
        ]
    }, version_str, release_notes, download_url, file_size


# **Feature: github-auto-update, Property 4: GitHub Response Parsing**
# **Validates: Requirements 1.2**
@given(response_data=github_release_response())
@settings(max_examples=100)
def test_property_github_response_parsing(response_data):
    """
    For any valid GitHub API release response, parsing SHALL extract version,
    release notes, download URL, and file size correctly.
    
    **Feature: github-auto-update, Property 4: GitHub Response Parsing**
    **Validates: Requirements 1.2**
    """
    data, expected_version, expected_notes, expected_url, expected_size = response_data
    
    checker = UpdateChecker("0.0.1", "owner/repo")
    update_info = checker._parse_github_response(data)
    
    assert update_info is not None, "Should parse valid response"
    assert update_info.latest_version == expected_version, \
        f"Version should be '{expected_version}', got '{update_info.latest_version}'"
    assert update_info.release_notes == expected_notes, \
        f"Release notes should match"
    assert update_info.download_url == expected_url, \
        f"Download URL should be '{expected_url}', got '{update_info.download_url}'"
    assert update_info.file_size == expected_size, \
        f"File size should be {expected_size}, got {update_info.file_size}"



# **Feature: github-auto-update, Property 5: Update Detection**
# **Validates: Requirements 1.3**
@given(
    current=version_tuple,
    latest=version_tuple
)
@settings(max_examples=100)
def test_property_update_detection(current, latest):
    """
    For any pair of current and latest versions where latest > current,
    the update checker SHALL return UpdateInfo indicating an update is available.
    
    **Feature: github-auto-update, Property 5: Update Detection**
    **Validates: Requirements 1.3**
    """
    current_str = version_tuple_to_string(current)
    latest_str = version_tuple_to_string(latest, with_prefix=True)  # GitHub uses v prefix
    
    # Create a mock response
    mock_response = {
        "tag_name": latest_str,
        "name": f"Version {latest_str}",
        "body": "Test release notes",
        "published_at": "2024-12-12T10:00:00Z",
        "assets": [
            {
                "name": "test.exe",
                "size": 1000000,
                "browser_download_url": f"https://github.com/owner/repo/releases/download/{latest_str}/test.exe"
            }
        ]
    }
    
    checker = UpdateChecker(current_str, "owner/repo")
    update_info = checker._parse_github_response(mock_response)
    
    assert update_info is not None, "Should parse valid response"
    
    # Check if update detection is correct
    from update.version_comparator import VersionComparator
    is_newer = VersionComparator.is_newer(update_info.latest_version, current_str)
    
    if latest > current:
        assert is_newer, \
            f"Should detect {latest_str} as newer than {current_str}"
    elif latest < current:
        assert not is_newer, \
            f"Should NOT detect {latest_str} as newer than {current_str}"
    else:
        assert not is_newer, \
            f"Same versions should not be detected as update"


# **Feature: github-auto-update, Property 6: Skipped Version Persistence**
# **Validates: Requirements 2.4**
@given(
    versions_to_skip=st.lists(version_tuple, min_size=1, max_size=5)
)
@settings(max_examples=100)
def test_property_skipped_version_persistence(versions_to_skip):
    """
    For any version marked as skipped, subsequent update checks SHALL not notify
    for that version unless force=True.
    
    **Feature: github-auto-update, Property 6: Skipped Version Persistence**
    **Validates: Requirements 2.4**
    """
    checker = UpdateChecker("0.0.1", "owner/repo")
    
    # Skip all versions
    for v in versions_to_skip:
        version_str = version_tuple_to_string(v)
        checker.skip_version(version_str)
    
    # Verify all versions are skipped
    for v in versions_to_skip:
        version_str = version_tuple_to_string(v)
        assert checker.is_version_skipped(version_str), \
            f"Version {version_str} should be skipped"
        
        # Also test with v prefix
        version_with_prefix = f"v{version_str}"
        assert checker.is_version_skipped(version_with_prefix), \
            f"Version {version_with_prefix} should also be skipped (normalized)"


# **Feature: github-auto-update, Property 6: Skipped Version Normalization**
# **Validates: Requirements 2.4**
@given(v=version_tuple)
@settings(max_examples=100)
def test_property_skipped_version_normalization(v):
    """
    For any version, skipping with or without 'v' prefix should result in the same
    normalized version being stored.
    
    **Feature: github-auto-update, Property 6: Skipped Version Persistence**
    **Validates: Requirements 2.4**
    """
    version_str = version_tuple_to_string(v)
    version_with_v = f"v{version_str}"
    version_with_V = f"V{version_str}"
    
    # Test skipping without prefix
    checker1 = UpdateChecker("0.0.1", "owner/repo")
    checker1.skip_version(version_str)
    
    assert checker1.is_version_skipped(version_str)
    assert checker1.is_version_skipped(version_with_v)
    assert checker1.is_version_skipped(version_with_V)
    
    # Test skipping with v prefix
    checker2 = UpdateChecker("0.0.1", "owner/repo")
    checker2.skip_version(version_with_v)
    
    assert checker2.is_version_skipped(version_str)
    assert checker2.is_version_skipped(version_with_v)
    assert checker2.is_version_skipped(version_with_V)


# Test for response without supported asset (.zip or .exe)
@given(
    version=version_tuple,
    unsupported_extension=st.sampled_from(['.tar.gz', '.dmg', '.deb', '.rpm', '.pkg'])
)
@settings(max_examples=100)
def test_property_github_response_no_supported_asset(version, unsupported_extension):
    """
    For any GitHub response without .zip or .exe asset, parsing SHALL return None.
    
    **Feature: github-auto-update, Property 4: GitHub Response Parsing**
    **Validates: Requirements 1.2**
    """
    version_str = version_tuple_to_string(version, with_prefix=True)
    
    mock_response = {
        "tag_name": version_str,
        "name": f"Version {version_str}",
        "body": "Test release notes",
        "published_at": "2024-12-12T10:00:00Z",
        "assets": [
            {
                "name": f"test{unsupported_extension}",
                "size": 1000000,
                "browser_download_url": f"https://github.com/owner/repo/releases/download/{version_str}/test{unsupported_extension}"
            }
        ]
    }
    
    checker = UpdateChecker("0.0.1", "owner/repo")
    update_info = checker._parse_github_response(mock_response)
    
    assert update_info is None, \
        f"Should return None when no .zip or .exe asset found (only {unsupported_extension})"


# Test for response with .zip asset (should be supported)
@given(version=version_tuple)
@settings(max_examples=50)
def test_property_github_response_zip_asset(version):
    """
    For any GitHub response with .zip asset, parsing SHALL return UpdateInfo.
    
    **Feature: github-auto-update, Property 4: GitHub Response Parsing**
    **Validates: Requirements 1.2**
    """
    version_str = version_tuple_to_string(version, with_prefix=True)
    
    mock_response = {
        "tag_name": version_str,
        "name": f"Version {version_str}",
        "body": "Test release notes",
        "published_at": "2024-12-12T10:00:00Z",
        "assets": [
            {
                "name": "CustomsBarcodeAutomation.zip",
                "size": 50000000,
                "browser_download_url": f"https://github.com/owner/repo/releases/download/{version_str}/CustomsBarcodeAutomation.zip"
            }
        ]
    }
    
    checker = UpdateChecker("0.0.1", "owner/repo")
    update_info = checker._parse_github_response(mock_response)
    
    assert update_info is not None, "Should return UpdateInfo when .zip asset found"
    assert update_info.download_url.endswith('.zip'), "Download URL should be for .zip file"
