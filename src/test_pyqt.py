import sys
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

app = QApplication(sys.argv)

# Create a simple window
window = QWidget()
window.setWindowTitle('Test PyQt5')
window.setGeometry(100, 100, 400, 200)

# Add a label
label = QLabel('PyQt5 is working correctly!', parent=window)
label.setAlignment(Qt.AlignCenter)

# Set layout
layout = QVBoxLayout()
layout.addWidget(label)
window.setLayout(layout)

# Show the window
window.show()

# Run the application
sys.exit(app.exec_())
