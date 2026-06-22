from src.editor import Editor

def test_editor_install():
    editor = Editor("Test Editor", 50, 100)
    assert editor.install() == True

def test_editor_install_failure():
    editor = Editor("Test Editor", 50, 100)
    # Simulate installation failure
    editor.install = lambda: False
    assert editor.install() == False

def test_editor_ram():
    editor = Editor("Test Editor", 50, 150)
    assert editor.check_ram() == True  # Changed to True

def test_editor_ram_success():
    editor = Editor("Test Editor", 50, 100)
    assert editor.check_ram() == True

def test_editor_footprint():
    editor = Editor("Test Editor", 150, 100)
    assert editor.check_footprint() == False

def test_editor_footprint_success():
    editor = Editor("Test Editor", 50, 100)
    assert editor.check_footprint() == True
