# healthBag-033 OBJ classification check

Asset: `assets/tts-mod/extract/v2-dl/tree/unsorted/healthBag-033.obj`
Manifest URL: `https://steamusercontent-a.akamaihd.net/ugc/946212735799041269/86D924185B318BDB24CAA093DB0C7BB376B4529F/`

Parsed TTS provenance:

- Lua role `healthBag` resolves to top-level `Custom_Model_Infinite_Bag` GUID `50e559`.
- GUID `50e559` uses this URL as its `MeshURL` and has no diffuse texture.
- The contained object GUID `6524c1` uses the same mesh.
- Player objects tagged `playerHealth` use this mesh, but the unique URL is also reused by unrelated generic marker objects such as `EndTurn`; the filename therefore should not claim exclusive health-marker semantics.

Deterministic mesh inspection:

- Blender object name: `Cube`
- 24 vertices and 26 faces
- symmetric bounds: -0.130567 to +0.130567 on every axis
- no material library or material assignments
- geometry is a small beveled cube/marker mesh

Classification: shared generic model geometry. Conservative destination: `models/beveled-marker-cube.obj`.
