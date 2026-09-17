# Included synthetic fixtures

Generated with Pillow/NumPy at 360×640, 25fps, 12 seconds. Files 01-clean and 02-faulty form a reference/defect pair. 03-intentional has the same video bytes as 02-faulty, but effects are labeled intentional and subtitles are clean. This deliberately isolates editorial intent. Not a real-world benchmark.

From repository root run `python -m cutguard scan examples/dummy-lab/media/02-faulty.mp4 --srt examples/dummy-lab/media/02-faulty.srt --out my-report`. See `ground-truth.json` for labels. Generated 0.2 results live in `examples/faulty-v020` and `examples/clean-v020`.
