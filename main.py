import sys
from json import dumps as js
from math import sqrt

from PyQt5 import QtWidgets

from ui import Ui_MainWindow, Ui_Region

POINT = tuple[float, float]


def inPolygon(x: float, y: float, points: list[tuple[float, float]]) -> bool:
    c = 0
    for i in range(1, len(points)):
        if (
            (points[i][1] <= y and y < points[i - 1][1])
            or (points[i - 1][1] <= y and y < points[i][1])
        ) and (
            x
            > (points[i - 1][0] - points[i][0])
            * (y - points[i][1])
            / (points[i - 1][1] - points[i][1])
            + points[i][0]
        ):
            c = 1 - c
    return bool(c)


class Region(QtWidgets.QWidget):
    ui: Ui_Region

    id: int

    def __init__(self) -> None:
        super().__init__()
        self.ui = Ui_Region()
        self.ui.setupUi(self)

    def set_id(self, id: int) -> None:
        self.id = id
        self.ui.editingRadio.setText(str(self.id + 1))


class MainWindow(QtWidgets.QMainWindow):
    ui: Ui_MainWindow

    regions: list[Region]

    def __init__(self) -> None:
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.regions = []

        self.ui.addButton.clicked.connect(self.add_region)

    def add_region(self) -> None:
        def unique() -> None:
            for r in self.regions:
                if r is not region:
                    r.ui.editingRadio.setChecked(False)

        def calculate() -> None:
            def polygon(points: list[tuple[float, float]]) -> None:
                page = self.ui.map.page()

                r = 30
                n = len(points)
                min_x = min(points[i][0] for i in range(n))
                max_x = max(points[i][0] for i in range(n))
                min_y = min(points[i][1] for i in range(n))
                max_y = max(points[i][1] for i in range(n))

                y = min_y
                k = 0
                while y < max_y:
                    x = min_x
                    if k:
                        x += r * sqrt(3) / 2
                    while x < max_x:
                        if inPolygon(x, y, points):
                            page.runJavaScript(
                                f"addCircle({js(region.id)},{js((x,y))},{js(r)})"
                            )
                        x += sqrt(3) * r
                    y += 3 * r / 2
                    k = 1 - k

            self.ui.map.page().runJavaScript(f"clearCircles({js(region.id)})")
            self.ui.map.page().runJavaScript(
                f"getCartesianPoints({js(region.id)});", polygon
            )

        def edit() -> None:
            self.ui.map.page().runJavaScript(
                f"editPolygon({js(region.id)},{js(region.ui.editingRadio.isChecked())});"
            )

        def delete() -> None:
            self.regions.remove(region)
            region.deleteLater()
            self.ui.map.page().runJavaScript(f"deletePolygon({js(region.id)});")

        region = Region()

        unique()

        self.regions.append(region)
        self.ui.regionsArea.widget().layout().insertWidget(0, region)
        self.ui.map.page().runJavaScript(f"addPolygon();", region.set_id)

        region.ui.calculateButton.clicked.connect(calculate)
        region.ui.editingRadio.toggled.connect(edit)
        region.ui.editingRadio.clicked.connect(unique)
        region.ui.deleteButton.clicked.connect(delete)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
