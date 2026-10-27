import json
from pathlib import Path
import struct
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from toolkit_sprite_codec import encode,decode,row_encode,HEADER,ENTRY


class SpriteCodecTests(unittest.TestCase):
    def sample(self):
        return encode([bytes([1,1,1,2,0,0,0,0]),bytes([1,1,1,3,0,0,0,0])],4,2,list(range(64)),[0,250],500,True)

    def test_known_key_and_skip_row_encodings(self):
        self.assertEqual(row_encode(bytes([3,3,3,7])),bytes([0x82,3,0,7]))
        self.assertEqual(row_encode(bytes([1,2,4]),bytes([1,2,3])),bytes([0x81,0,4]))

    def test_two_rows_and_delta_round_trip(self):
        out=decode(self.sample())
        self.assertEqual(out['frames'][1],bytes([1,1,1,3,0,0,0,0]))
        self.assertEqual(out['times'],[0,250]);self.assertTrue(out['loop'])

    def test_frame_checksum_rejects_corruption(self):
        data=bytearray(self.sample());data[-1]^=1
        with self.assertRaises(ValueError):decode(data)

    def test_truncated_index_or_payload_rejected(self):
        for length in (0,23,151,len(self.sample())-1):
            with self.assertRaises(ValueError):decode(self.sample()[:length])

    def test_row_overflow_rejected(self):
        data=bytearray(self.sample());entry=ENTRY.unpack_from(data,HEADER.size+128)
        offset=entry[1];row=struct.unpack_from('<I',data,offset)[0]
        data[offset+row]=0xff
        with self.assertRaises(ValueError):decode(data)

    def test_first_frame_must_be_key(self):
        data=bytearray(self.sample());struct.pack_into('<I',data,HEADER.size+128+16,0)
        with self.assertRaises(ValueError):decode(data)

    def test_palette_index_and_timestamp_bounds(self):
        with self.assertRaises(ValueError):encode([bytes([64])],1,1,list(range(64)),[0],100)
        with self.assertRaises(ValueError):encode([bytes([1])],1,1,list(range(64)),[100],100)

    def test_all_production_assets_decode_and_fit_budget(self):
        manifest=json.loads((ROOT/'game-art/toolkit/sprites/manifest.json').read_text())
        total=0
        for clip in manifest['clips'].values():
            for variant in clip['variants'].values():
                raw=(ROOT/variant['binary']).read_bytes();total+=len(raw)
                result=decode(raw)
                self.assertEqual(result['times'],clip['times'])
                self.assertEqual(len(result['palette']),64)
                self.assertTrue(all(max(frame)<64 for frame in result['frames']))
        self.assertEqual(total,manifest['binary_bytes']);self.assertLessEqual(total,1024*1024)


if __name__=='__main__':unittest.main()
