"""Pure validation tests for the future app-only installer; never opens a port."""
import hashlib
import importlib.util
from pathlib import Path
import struct
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'firmware/tools'))
import flash_candidate as F

def table(changes=None,flags=0,layout=None):
    values=dict(F.EXPECTED if layout is None else layout)
    values.update(changes or {})
    raw=b''.join(struct.pack('<HBBII16sI',0x50aa,t,s,o,n,label.encode(),flags) for label,(t,s,o,n) in values.items())
    return (raw+b'\xeb\xeb'+b'\xff'*14+hashlib.md5(raw).digest()).ljust(0xc00,b'\xff')

def app():
    raw=bytearray(256); raw[0]=0xe9; struct.pack_into('<H',raw,12,5); return bytes(raw)

class FlashGuardTests(unittest.TestCase):
    def test_exact_app_hash_and_c3_are_required(self):
        data=app(); F.validate_app(data,F.digest(data))
        for sha in ['0'*64,F.digest(data).upper(),'xyz']:
            with self.assertRaises(ValueError): F.validate_app(data,sha)
        wrong=bytearray(data); wrong[12]=9
        with self.assertRaises(ValueError): F.validate_app(wrong,F.digest(wrong))
    def test_invalid_app_magic_size_and_partition_crossing_are_rejected(self):
        for data in [b'',b'\xe9'*200,b'\0'*256,app()+b'\0'*F.APP_SIZE]:
            with self.assertRaises(ValueError): F.validate_app(data,F.digest(data))
    def test_exact_partition_map_is_accepted_and_wrong_layout_is_rejected(self):
        F.validate_layout(table())
        for changes in [{'factory':(0,0,0x10000,0x7f0000)}, {'nvs':(1,2,0x9000,0x5000)}]:
            with self.assertRaises(ValueError): F.validate_layout(table(changes))
    def test_partition_md5_truncation_and_flags_are_rejected(self):
        raw=bytearray(table()); raw[20]^=1
        for data in [raw,table()[:100],table(flags=1)]:
            with self.assertRaises(ValueError): F.validate_layout(data)
    def test_measured_legacy_adventure_layout_is_accepted_without_repartitioning(self):
        self.assertEqual(F.validate_layout(table(layout=F.LEGACY_ADVENTURE)),0x1f0000)
        data=app(); F.validate_app(data,F.digest(data),0x1f0000)
    def test_words_layout_keeps_record_and_assets_beyond_erase_boundary(self):
        self.assertEqual(F.validate_layout(table(layout=F.WORDS)),0x1f0000)
        self.assertEqual(F.WORDS['record'][2],0x200000)
        data=app()+b'\0'*(0x1f0000-256)
        F.validate_app(data,F.digest(data),F.validate_layout(table(layout=F.WORDS)))
        too_large=data+b'\0'
        with self.assertRaises(ValueError): F.validate_app(too_large,F.digest(too_large),0x1f0000)
        changed=dict(F.WORDS);changed['record']=(1,0x40,0x1ff000,0x10000)
        with self.assertRaises(ValueError): F.validate_layout(table(layout=changed))
    def test_candidate_must_fit_the_actual_smaller_legacy_partition(self):
        data=app()+b'\0'*0x200000
        F.validate_app(data,F.digest(data))
        with self.assertRaises(ValueError): F.validate_app(data,F.digest(data),F.validate_layout(table(layout=F.LEGACY_ADVENTURE)))
        changed=dict(F.LEGACY_ADVENTURE); changed['factory']=(0,0,0x10000,0x200000)
        with self.assertRaises(ValueError): F.validate_layout(table(layout=changed))
    def test_wrong_device_security_or_flash_size_is_rejected(self):
        class Device:
            CHIP_NAME='ESP32-C3'; flash=0x170000; secure=False
            def read_mac(self): return bytes(range(6))
            def flash_id(self): return self.flash
            def get_security_info(self): return {'parsed_flags':{'SECURE_BOOT_EN':self.secure},'flash_crypt_cnt':0}
        d=Device(); mac='00:01:02:03:04:05'; F.check_device(d,mac)
        with self.assertRaises(ValueError): F.check_device(d,'00:01:02:03:04:06')
        d.CHIP_NAME='ESP32-S3'
        with self.assertRaises(ValueError): F.check_device(d,mac)
        d.CHIP_NAME='ESP32-C3'; d.secure=True
        with self.assertRaises(ValueError): F.check_device(d,mac)
        d.secure=False; d.flash=0x180000
        with self.assertRaises(ValueError): F.check_device(d,mac)
