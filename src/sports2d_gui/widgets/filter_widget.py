from __future__ import annotations

from typing import Any
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDoubleSpinBox, QFormLayout, QGroupBox, QSpinBox, QStackedWidget, QVBoxLayout, QWidget,
)

FILTERS = [
    ("butterworth", "Butterworth Low-pass Filter"),
    ("kalman", "Kalman Filter"),
    ("one_euro", "1-Euro Filter"),
    ("gcv_spline", "GCV Spline Filter"),
    ("acc_minimizing", "Acceleration Minimizing Filter"),
    ("gaussian", "Gaussian Filter"),
    ("loess", "LOESS Filter"),
    ("median", "Median Filter"),
    ("butterworth_on_speed", "Butterworth on Speed Filter"),
]


class FilterConfigWidget(QWidget):
    filterChanged = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Main filter type selector
        form = QFormLayout()
        self.combo_type = QComboBox()
        for f_id, f_name in FILTERS:
            self.combo_type.addItem(f"{f_name} ({f_id})", f_id)

        form.addRow("フィルタ種類:", self.combo_type)
        layout.addLayout(form)

        # Stacked widget for parameters
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        # 1. Butterworth
        w_bw = QWidget()
        f_bw = QFormLayout(w_bw)
        self.bw_cutoff = QDoubleSpinBox(); self.bw_cutoff.setRange(0.1, 100.0); self.bw_cutoff.setValue(6.0)
        self.bw_order = QSpinBox(); self.bw_order.setRange(1, 10); self.bw_order.setValue(4)
        f_bw.addRow("カットオフ周波数 [Hz]:", self.bw_cutoff)
        f_bw.addRow("次数 (Order):", self.bw_order)
        self.stack.addWidget(w_bw)

        # 2. Kalman
        w_km = QWidget()
        f_km = QFormLayout(w_km)
        self.km_trust = QDoubleSpinBox(); self.km_trust.setRange(0.1, 100000.0); self.km_trust.setValue(500.0)
        self.km_smooth = QCheckBox("Smoother を適用"); self.km_smooth.setChecked(True)
        f_km.addRow("Trust Ratio:", self.km_trust)
        f_km.addRow("Smooth:", self.km_smooth)
        self.stack.addWidget(w_km)

        # 3. 1-Euro
        w_oe = QWidget()
        f_oe = QFormLayout(w_oe)
        self.oe_fc = QDoubleSpinBox(); self.oe_fc.setRange(0.01, 100.0); self.oe_fc.setValue(4.0)
        self.oe_beta = QDoubleSpinBox(); self.oe_beta.setRange(0.0, 100.0); self.oe_beta.setValue(1.5)
        self.oe_dfc = QDoubleSpinBox(); self.oe_dfc.setRange(0.01, 100.0); self.oe_dfc.setValue(1.0)
        f_oe.addRow("Min Cutoff (fc):", self.oe_fc)
        f_oe.addRow("Beta (Speed coefficient):", self.oe_beta)
        f_oe.addRow("Deriv Cutoff (d_fc):", self.oe_dfc)
        self.stack.addWidget(w_oe)

        # 4. GCV Spline
        w_gcv = QWidget()
        f_gcv = QFormLayout(w_gcv)
        self.gcv_sf = QDoubleSpinBox(); self.gcv_sf.setRange(0.0, 100.0); self.gcv_sf.setValue(1.0)
        f_gcv.addRow("Smoothing Factor:", self.gcv_sf)
        self.stack.addWidget(w_gcv)

        # 5. Acc Minimizing
        w_am = QWidget()
        f_am = QFormLayout(w_am)
        self.am_fc = QDoubleSpinBox(); self.am_fc.setRange(0.1, 100.0); self.am_fc.setValue(6.0)
        f_am.addRow("Acc Minimizing Cutoff:", self.am_fc)
        self.stack.addWidget(w_am)

        # 6. Gaussian
        w_ga = QWidget()
        f_ga = QFormLayout(w_ga)
        self.ga_sigma = QSpinBox(); self.ga_sigma.setRange(1, 50); self.ga_sigma.setValue(1)
        f_ga.addRow("Sigma Kernel Size:", self.ga_sigma)
        self.stack.addWidget(w_ga)

        # 7. LOESS
        w_lo = QWidget()
        f_lo = QFormLayout(w_lo)
        self.lo_nb = QSpinBox(); self.lo_nb.setRange(3, 100); self.lo_nb.setValue(5)
        f_lo.addRow("Number of Values Used:", self.lo_nb)
        self.stack.addWidget(w_lo)

        # 8. Median
        w_med = QWidget()
        f_med = QFormLayout(w_med)
        self.med_kernel = QSpinBox(); self.med_kernel.setRange(3, 99); self.med_kernel.setSingleStep(2); self.med_kernel.setValue(3)
        f_med.addRow("Kernel Size (奇数):", self.med_kernel)
        self.stack.addWidget(w_med)

        # 9. Butterworth on Speed
        w_bws = QWidget()
        f_bws = QFormLayout(w_bws)
        self.bws_fc = QDoubleSpinBox(); self.bws_fc.setRange(0.1, 100.0); self.bws_fc.setValue(6.0)
        self.bws_order = QSpinBox(); self.bws_order.setRange(1, 10); self.bws_order.setValue(4)
        f_bws.addRow("Speed Cutoff [Hz]:", self.bws_fc)
        f_bws.addRow("Speed Order:", self.bws_order)
        self.stack.addWidget(w_bws)

        self.combo_type.currentIndexChanged.connect(self._on_type_changed)
        self._on_type_changed(0)

    def _on_type_changed(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        self.filterChanged.emit()

    def get_filter_type(self) -> str:
        return self.combo_type.currentData()

    def set_filter_type(self, filter_type: str) -> None:
        for i in range(self.combo_type.count()):
            if self.combo_type.itemData(i) == filter_type:
                self.combo_type.setCurrentIndex(i)
                break

    def get_params_dict(self) -> dict[str, Any]:
        filter_type = self.get_filter_type()
        params: dict[str, Any] = {"filter_type": filter_type}

        if filter_type == "butterworth":
            params["butterworth"] = {
                "cut_off_frequency": self.bw_cutoff.value(),
                "order": self.bw_order.value(),
            }
        elif filter_type == "kalman":
            params["kalman"] = {
                "trust_ratio": self.km_trust.value(),
                "smooth": self.km_smooth.isChecked(),
            }
        elif filter_type == "one_euro":
            params["one_euro"] = {
                "oneeuro_cut_off_frequency": self.oe_fc.value(),
                "oneeuro_beta": self.oe_beta.value(),
                "oneeuro_d_cut_off_frequency": self.oe_dfc.value(),
            }
        elif filter_type == "gcv_spline":
            params["gcv_spline"] = {
                "gcv_cut_off_frequency": "auto",
                "gcv_smoothing_factor": self.gcv_sf.value(),
            }
        elif filter_type == "acc_minimizing":
            params["acc_minimizing"] = {
                "accminimizing_cut_off_frequency": self.am_fc.value(),
            }
        elif filter_type == "gaussian":
            params["gaussian"] = {
                "sigma_kernel": self.ga_sigma.value(),
            }
        elif filter_type == "loess":
            params["loess"] = {
                "nb_values_used": self.lo_nb.value(),
            }
        elif filter_type == "median":
            params["median"] = {
                "kernel_size": self.med_kernel.value(),
            }
        elif filter_type == "butterworth_on_speed":
            params["butterworth_on_speed"] = {
                "butterspeed_cut_off_frequency": self.bws_fc.value(),
                "butterspeed_order": self.bws_order.value(),
            }

        return params

    def set_params_dict(self, cfg: dict[str, Any]) -> None:
        ftype = cfg.get("filter_type", "butterworth")
        self.set_filter_type(ftype)

        bw = cfg.get("butterworth", {})
        if "cut_off_frequency" in bw: self.bw_cutoff.setValue(float(bw["cut_off_frequency"]))
        if "order" in bw: self.bw_order.setValue(int(bw["order"]))

        km = cfg.get("kalman", {})
        if "trust_ratio" in km: self.km_trust.setValue(float(km["trust_ratio"]))
        if "smooth" in km: self.km_smooth.setChecked(bool(km["smooth"]))

        oe = cfg.get("one_euro", {})
        if "oneeuro_cut_off_frequency" in oe: self.oe_fc.setValue(float(oe["oneeuro_cut_off_frequency"]))
        if "oneeuro_beta" in oe: self.oe_beta.setValue(float(oe["oneeuro_beta"]))
        if "oneeuro_d_cut_off_frequency" in oe: self.oe_dfc.setValue(float(oe["oneeuro_d_cut_off_frequency"]))

        gcv = cfg.get("gcv_spline", {})
        if "gcv_smoothing_factor" in gcv: self.gcv_sf.setValue(float(gcv["gcv_smoothing_factor"]))

        am = cfg.get("acc_minimizing", {})
        if "accminimizing_cut_off_frequency" in am: self.am_fc.setValue(float(am["accminimizing_cut_off_frequency"]))

        ga = cfg.get("gaussian", {})
        if "sigma_kernel" in ga: self.ga_sigma.setValue(int(ga["sigma_kernel"]))

        lo = cfg.get("loess", {})
        if "nb_values_used" in lo: self.lo_nb.setValue(int(lo["nb_values_used"]))

        med = cfg.get("median", {})
        if "kernel_size" in med: self.med_kernel.setValue(int(med["kernel_size"]))

        bws = cfg.get("butterworth_on_speed", {})
        if "butterspeed_cut_off_frequency" in bws: self.bws_fc.setValue(float(bws["butterspeed_cut_off_frequency"]))
        if "butterspeed_order" in bws: self.bws_order.setValue(int(bws["order"] if "order" in bws else bws.get("butterspeed_order", 4)))
