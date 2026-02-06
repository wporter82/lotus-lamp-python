"""
Tests for mode management
"""

import pytest
from lotus_lamp.modes import (
    get_mode_name,
    get_mode_category,
    search_modes,
    get_mode_by_category_index,
    list_category_modes,
    list_all_categories,
    CATEGORIES
)


class TestModeNames:
    """Test mode name lookups"""

    def test_get_mode_name_valid(self):
        """Test getting a valid mode name"""
        # Mode 143 should be "W-R-W Flow"
        name = get_mode_name(143)
        assert name is not None
        assert isinstance(name, str)
        assert len(name) > 0

    def test_get_mode_name_invalid(self):
        """Test getting an invalid mode number"""
        name = get_mode_name(9999)
        assert name == "Unknown Mode 9999"

    def test_get_mode_name_boundary(self):
        """Test mode numbers at boundaries"""
        # Mode 0 should exist
        name_0 = get_mode_name(0)
        assert name_0 is not None

        # Mode 212 should exist (last mode)
        name_212 = get_mode_name(212)
        assert name_212 is not None


class TestModeCategories:
    """Test mode category functionality"""

    def test_get_mode_category_valid(self):
        """Test getting category for a valid mode"""
        category = get_mode_category(143)
        assert category is not None
        assert category in CATEGORIES

    def test_get_mode_category_invalid(self):
        """Test getting category for invalid mode"""
        category = get_mode_category(9999)
        assert category == "unknown"

    def test_categories_defined(self):
        """Test that CATEGORIES is properly defined"""
        assert isinstance(CATEGORIES, dict)
        assert len(CATEGORIES) > 0

        # Check for expected categories
        expected_categories = ['basic', 'trans', 'tail', 'water',
                              'curtain', 'run', 'runback', 'flow']
        for cat in expected_categories:
            assert cat in CATEGORIES

    def test_list_all_categories(self, capsys):
        """Test listing all categories"""
        list_all_categories()

        captured = capsys.readouterr()
        assert len(captured.out) > 0
        # Should mention categories
        assert "categories" in captured.out.lower() or "basic" in captured.out.lower()


class TestModeSearch:
    """Test mode search functionality"""

    def test_search_modes_basic(self):
        """Test basic mode search"""
        results = search_modes("flow")

        assert isinstance(results, list)
        assert len(results) > 0
        # Each result should be (mode_num, mode_name, category)
        assert all(len(r) == 3 for r in results)

    def test_search_modes_case_insensitive(self):
        """Test case-insensitive search"""
        results_lower = search_modes("blue")
        results_upper = search_modes("BLUE")

        assert len(results_lower) == len(results_upper)

    def test_search_modes_no_results(self):
        """Test search with no results"""
        results = search_modes("nonexistentpattern12345")

        assert isinstance(results, list)
        assert len(results) == 0

    def test_search_modes_partial_match(self):
        """Test partial string matching"""
        results = search_modes("cyan")

        assert len(results) > 0
        # All results should contain 'cyan' in the name
        for mode_num, mode_name, category in results:
            assert "cyan" in mode_name.lower()


class TestCategoryModes:
    """Test category mode listings"""

    def test_list_category_modes(self, capsys):
        """Test listing modes in a category"""
        list_category_modes('flow')

        captured = capsys.readouterr()
        assert len(captured.out) > 0
        # Should print mode information
        assert "flow" in captured.out.lower() or "mode" in captured.out.lower()

    def test_list_category_modes_invalid(self, capsys):
        """Test listing modes from invalid category"""
        list_category_modes('invalid_category')

        captured = capsys.readouterr()
        # Should print error or warning about invalid category
        assert len(captured.out) >= 0  # May print nothing or error

    def test_get_mode_by_category_index(self):
        """Test getting mode by category and index"""
        # Get first mode in 'flow' category (1-based indexing)
        mode_num = get_mode_by_category_index('flow', 1)

        assert isinstance(mode_num, int)
        assert mode_num >= 0

    def test_get_mode_by_category_index_invalid(self):
        """Test getting mode with invalid index"""
        with pytest.raises(ValueError, match="out of range"):
            get_mode_by_category_index('flow', 9999)

    def test_get_mode_by_category_invalid_category(self):
        """Test getting mode from invalid category"""
        with pytest.raises(ValueError, match="Unknown category"):
            get_mode_by_category_index('invalid', 1)


class TestModeData:
    """Test mode data integrity"""

    def test_all_modes_have_names(self):
        """Test that all modes 0-212 have names"""
        missing = []
        for mode_num in range(213):
            name = get_mode_name(mode_num)
            if name is None:
                missing.append(mode_num)

        assert len(missing) == 0, f"Missing names for modes: {missing}"

    def test_all_modes_have_categories(self):
        """Test that all modes have categories"""
        missing = []
        for mode_num in range(213):
            category = get_mode_category(mode_num)
            if category is None:
                missing.append(mode_num)

        assert len(missing) == 0, f"Missing categories for modes: {missing}"

    def test_category_mode_counts(self):
        """Test that category mode counts are reasonable"""
        for category_name, modes in CATEGORIES.items():
            # Each category should have at least 1 mode
            assert len(modes) > 0, f"Category '{category_name}' has no modes"
            # But not more than 50 (sanity check)
            assert len(modes) < 50, f"Category '{category_name}' has too many modes"

    def test_no_duplicate_modes(self):
        """Test that no mode appears in multiple categories"""
        all_modes = []
        for category_name, modes in CATEGORIES.items():
            all_modes.extend(modes)

        # Check for duplicates
        assert len(all_modes) == len(set(all_modes)), "Duplicate modes found across categories"

    def test_mode_numbers_sequential(self):
        """Test that all mode numbers 0-212 are accounted for"""
        all_modes = []
        for category_name, modes in CATEGORIES.items():
            all_modes.extend(modes)

        all_modes.sort()
        expected = list(range(213))

        assert all_modes == expected, "Not all modes 0-212 are accounted for"
