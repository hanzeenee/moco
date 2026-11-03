"""Build-only helper: python -m pip install 'fonttools[woff]==4.68.0'.

Normal npm builds only verify committed assets using Node; they do not need Python.
"""
from pathlib import Path
import hashlib
import json
import subprocess

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen

frontend = Path(__file__).resolve().parent.parent
subprocess.run(['node', 'scripts/check-icon-subset.cjs', '--prepare'], cwd=frontend, check=True)
assets = frontend / 'src/assets/fonts'
manifest_file = assets / 'icons-manifest.json'
manifest = json.loads(manifest_file.read_text(encoding='utf-8'))
source = frontend / 'node_modules/@mdi/font/fonts/materialdesignicons-webfont.woff2'
output = assets / 'moconix-icons.woff2'
codepoints = {int(code, 16) for code in manifest['icons'].values()}

options = subset.Options()
options.flavor = 'woff2'
options.hinting = True
options.recalc_bounds = False
options.recalc_timestamp = False
options.glyph_names = True
options.notdef_outline = True
font = subset.load_font(str(source), options)
subsetter = subset.Subsetter(options=options)
subsetter.populate(unicodes=codepoints)
subsetter.subset(font)
subset.save_font(font, str(output), options)

# Verify every included glyph's exact contours, advance width and hinting program.
original = TTFont(source)
result = TTFont(output)
assert set(result.getBestCmap()) >= codepoints
for point in sorted(codepoints):
    original_name = original.getBestCmap()[point]
    result_name = result.getBestCmap()[point]
    before, after = RecordingPen(), RecordingPen()
    original.getGlyphSet()[original_name].draw(before)
    result.getGlyphSet()[result_name].draw(after)
    assert before.value == after.value, f'Contour changed: U+{point:X}'
    assert original['hmtx'][original_name] == result['hmtx'][result_name]
    before_glyph = original['glyf'][original_name]
    after_glyph = result['glyf'][result_name]
    if hasattr(before_glyph, 'program'):
        assert before_glyph.program.getBytecode() == after_glyph.program.getBytecode()
for table, names in {'head': ['unitsPerEm'], 'hhea': ['ascent', 'descent', 'lineGap'],
                     'OS/2': ['sTypoAscender', 'sTypoDescender', 'sTypoLineGap', 'usWinAscent', 'usWinDescent']}.items():
    for name in names:
        assert getattr(original[table], name) == getattr(result[table], name)

manifest['subsetSha256'] = hashlib.sha256(output.read_bytes()).hexdigest()
manifest['glyphCount'] = len(codepoints)
manifest['sourceBytes'] = source.stat().st_size
manifest['subsetBytes'] = output.stat().st_size
manifest['generator'] = 'fonttools[woff] 4.68.0'
manifest_file.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8', newline='\n')
(assets / 'LICENSE-mdi.txt').write_bytes((frontend / 'node_modules/@mdi/font/LICENSE').read_bytes())
print(f'Exact contours, metrics and hinting verified: {len(codepoints)} glyphs, {source.stat().st_size:,} -> {output.stat().st_size:,} bytes.')
subprocess.run(['node', 'scripts/check-icon-subset.cjs'], cwd=frontend, check=True)
