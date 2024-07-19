# -*- coding: utf-8 -*-

import logging

from .test_tec_base import TestTecCommon

_logger = logging.getLogger(__name__)


class TestTecConfig(TestTecCommon):
    """Test module configuration and its effects on tecs."""

    @classmethod
    def setUpClass(cls):
        super(TestTecConfig, cls).setUpClass()
        cls.Tec = cls.env["tec.tec"]
        cls.Settings = cls.env["res.config.settings"]
        cls.features = (
            # Pairs of associated (config_flag, tec_flag)
            ("group_subtask_tec", "allow_subtasks"),
            ("group_tec_recurring_tasks", "allow_recurring_tasks"),
            ("group_tec_rating", "rating_active"),
            )

        # Start with a known value on feature flags to ensure validity of tests
        cls._set_feature_status(is_enabled=False)

    @classmethod
    def _set_feature_status(cls, is_enabled):
        """Set enabled/disabled status of all optional features in the
        tec app config to is_enabled (boolean).
        """
        features_config = cls.Settings.create(
            {feature[0]: is_enabled for feature in cls.features})
        features_config.execute()

    def test_existing_tecs_enable_features(self):
        """Check that *existing* tecs have features enabled when
        the user enables them in the module configuration.
        """
        self._set_feature_status(is_enabled=True)
        for config_flag, tec_flag in self.features:
            self.assertTrue(
                self.tec_pigs[tec_flag],
                "Existing tec failed to adopt activation of "
                f"{config_flag}/{tec_flag} feature")

    def test_new_tecs_enable_features(self):
        """Check that after the user enables features in the module
        configuration, *newly created* tecs have those features
        enabled as well.
        """
        self._set_feature_status(is_enabled=True)
        tec_cows = self.Tec.create({
            "name": "Cows",
            "partner_id": self.partner_1.id})
        for config_flag, tec_flag in self.features:
            self.assertTrue(
                tec_cows[tec_flag],
                f"Newly created tec failed to adopt activation of "
                f"{config_flag}/{tec_flag} feature")
