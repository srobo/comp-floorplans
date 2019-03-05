#! /bin/bash
for layout in layouts/*.yaml; do
    echo "## $(basename $layout)"
    python3 generate_svg.py $(basename $layout)
done