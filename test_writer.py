import pandoc

import writer


def test_is_task_list():
    content = """
- [ ] item
    - [ ] nested item
- [x] item
    """
    doc = pandoc.read(source=content, format="markdown")

    assert writer.is_task_list(doc[1][0])

    content = """
- item
    - nested item
- item
    """
    doc = pandoc.read(source=content, format="markdown")

    assert not writer.is_task_list(doc[1][0])

def test_fail():
    content = """- this is not"""
    doc = pandoc.read(source=content, format="markdown")

    assert not writer.is_task_list(doc[1][0])
