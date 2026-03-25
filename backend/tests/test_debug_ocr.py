"""
Debug test to trace where duplicates come from.
"""

import asyncio
import sys

sys.path.insert(0, "backend")

from services.ocr.gemini import GeminiVisionClient


import pytest

@pytest.mark.asyncio
async def test_ocr_output():
    """Test OCR and print detailed output."""
    client = GeminiVisionClient()

    if not client.available:
        print("Gemini client not available!")
        return

    # Use a test image
    test_image = (
        "backend/uploads/pages/72c10856-a817-4b95-8982-46f9e37e8cfd/page_001.png"
    )

    print("=" * 60)
    print("TESTING OCR OUTPUT")
    print("=" * 60)

    result = await client.recognize(test_image)

    print(f"\n=== TEXT OUTPUT ===")
    print(result.text[:500] if result.text else "No text")

    print(f"\n=== LATEX OUTPUT ===")
    if result.latex:
        # Split by separator
        if "\xa7\xa7\xa7" in result.latex:
            lines = result.latex.split("\xa7\xa7\xa7")
            print(f"Found {len(lines)} lines with separator")
            for i, line in enumerate(lines[:10]):
                print(f"  {i+1}. {line[:60]}...")
        else:
            print("NO SEPARATOR FOUND!")
            print(result.latex[:500])
    else:
        print("No latex")

    print(f"\n=== CHECKING FOR DUPLICATES ===")
    if result.latex:
        import re

        # Find all task IDs
        pattern = re.compile(r"(\d+[a-z]?)\)", re.IGNORECASE)
        matches = list(pattern.finditer(result.latex))

        task_counts = {}
        for match in matches:
            task_id = match.group(1).lower()
            task_counts[task_id] = task_counts.get(task_id, 0) + 1

        print(f"Task ID counts:")
        for task_id, count in sorted(task_counts.items()):
            status = "DUPLICATE!" if count > 1 else "OK"
            print(f"  {task_id}: {count} - {status}")


if __name__ == "__main__":
    asyncio.run(test_ocr_output())
