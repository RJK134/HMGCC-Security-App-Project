"""Tests for source tier classification."""

from core.models.document import SourceTier
from core.validation.source_tier import SourceTierClassifier


class TestSourceTierClassifier:
    """Tests for SourceTierClassifier."""

    def setup_method(self) -> None:
        self.classifier = SourceTierClassifier()

    def test_datasheet_classified_tier1(self) -> None:
        result = self.classifier.classify_from_metadata("STM32F407_datasheet.pdf", {})
        assert result == SourceTier.TIER_1_MANUFACTURER

    def test_manual_classified_tier1(self) -> None:
        result = self.classifier.classify_from_metadata("user_manual_v2.pdf", {})
        assert result == SourceTier.TIER_1_MANUFACTURER

    def test_manufacturer_in_author_tier1(self) -> None:
        result = self.classifier.classify_from_metadata(
            "product_info.pdf", {"author": "STMicroelectronics"},
        )
        assert result == SourceTier.TIER_1_MANUFACTURER

    def test_ieee_paper_tier2(self) -> None:
        result = self.classifier.classify_from_metadata("ieee_modbus_security.pdf", {})
        assert result == SourceTier.TIER_2_ACADEMIC

    def test_doi_in_metadata_tier2(self) -> None:
        result = self.classifier.classify_from_metadata(
            "research.pdf", {"doi": "10.1109/TEST.2024.001"},
        )
        assert result == SourceTier.TIER_2_ACADEMIC

    def test_stackoverflow_tier3(self) -> None:
        result = self.classifier.classify_from_metadata(
            "stackoverflow_gpio_question.html", {},
        )
        assert result == SourceTier.TIER_3_TRUSTED_FORUM

    def test_unknown_file_tier4(self) -> None:
        result = self.classifier.classify_from_metadata("random_notes.txt", {})
        assert result == SourceTier.TIER_4_UNVERIFIED

    def test_tier_weights(self) -> None:
        assert self.classifier.get_tier_weight(SourceTier.TIER_1_MANUFACTURER) == 1.0
        assert self.classifier.get_tier_weight(SourceTier.TIER_2_ACADEMIC) == 0.8
        assert self.classifier.get_tier_weight(SourceTier.TIER_3_TRUSTED_FORUM) == 0.5
        assert self.classifier.get_tier_weight(SourceTier.TIER_4_UNVERIFIED) == 0.3

    def test_tier_labels(self) -> None:
        label = self.classifier.get_tier_label(SourceTier.TIER_1_MANUFACTURER)
        assert "Manufacturer" in label
