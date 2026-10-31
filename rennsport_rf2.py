#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rennsport -> rFactor 2 Physik-Konverter
========================================

Liest die Fahrzeugphysik aus den entpackten Rennsport-Dateien (rennsport_unpak.py)
und schreibt sie als rFactor-2-Dateien:

    <Auto>.hdv            Fahrzeug (General, Aero, Fahrwerk, Controls, Antrieb, Raeder)
    <Auto>_Chassis.ini    Rigid Bodies + Constraints
    <Auto>_Engine.ini     Motor
    <Auto>_Gears.ini      Getriebe
    <Auto>.tbc            Reifen (Slip-Kurven + Compounds)
    <Reifen>.tgm          Reifenmodell (Struktur, Realtime, Lookup)

Benutzung:
    python rennsport_rf2.py BMW_M4_GT3_2022 -o rF2_Export
    python rennsport_rf2.py "...\\Content\\Blueprints\\Configs\\Cars\\BMW\\BMW_M4_GT3_2022" -o rF2_Export
    python rennsport_rf2.py --list
    python rennsport_rf2.py --all -o rF2_Export     -> alle Fahrzeuge
    python rennsport_rf2.py BMW_M4_GT3_2022 --json      -> zusaetzlich kompletter JSON-Dump

Beim ersten Start wird nach dem entpackten Content-Ordner gefragt
(gespeichert in rennsport_rf2.ini). Keine zusaetzlichen Pakete noetig.

Das eingebettete Schema (Property-Namen und -Typen) wurde aus der Reflection
der Rennsport-Exe gewonnen; die Exe selbst wird nicht benoetigt.
"""

import argparse
import base64
import configparser
import glob
import json
import os
import re
import struct
import sys
import zlib

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INI_PATH = os.path.join(SCRIPT_DIR, "rennsport_rf2.ini")

SCHEMA = json.loads(zlib.decompress(base64.b64decode("""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
PQ/WYyhT9B1ZwNPND8g5MnGrE0izNgekh9P7jfhM0889Eney3xiQzQBTBYG/UjzMdMeRV7RJZmO0piJZeUQLiyeNr7QuFzRNRDdE
cJ9gAdFRVlJt3YWs5lZDXh0FUv++af2OxoiBLwVi1kXhZa6RCMfguImAmfc3I2DhZ8kImYfjMSLuPUxZQQsoFu9SvTqRB+pdqXDv
sIBiatdNuqHnbtvrI3jc07SidMcA+75huIPVOE26ABuSLGJW8MhcAqcQbG0abxDravTD8beIq0F59IUbjt0Mp03nOBr2bmkARLlT
elW8rluiudWQmwLEJe2waKs/rPwCZqiSeMEQQOcGM+3/+Cq7WpTpagJ/q78dorNpoWGQj7D9gI620XJ5nYYciVVJSR96pNe+wWDi
tb9MyoDN7vm8AhtCKK239HUQiWZNR/kxqHPSwDuHK12iRcNBqSHeQMlcEfgrHRVDiG8EqhWnMkHh2SFj0XwUQGCezpl+qXDrrTH+
laZjyDCRHNz9DIDaDjt1TMEv1/4ikNnFbOrutItTy4+d00SJCrZ9U7OVoRuVzTzXnTER1QZ9GbD1bNzWjnV9H2aWcxeT8jjcpnDo
IFutNFVK47DxGEGDhzTpbmHR4X4aIGBEwP0+lZhoQXolwhiUoW+dxI1eQVGAYWtlux531MHG7eu1n+yMj2VsJuMCjltbvmqbr6tO
sO18vavwRWBnccKKeO+/OdvXnKnM7uh7sSUzl5zDi43bvF/IMOHRSVwqsUy4SmlGCmp9MoHp4FaIloKbLpZUnfN1KgOydoOu451F
5kvglBvwbKAFzzhzbttv5GViDlgz//EL86NtWmNBMvbi6JxnGdqOYqRD6Z683pH6Cq4fePPkw9P3R4+7rhuhnSxrXvNmlv+EBMt6
LPmwjVd2EM0x1ygHam2L5D9057/H7/Ta9HkANzWqPCEMkmapmkeu1d2H5SizNlQe45EdYxYohoJgVmaMZ5EkMdFjFiLooi1GD6Ax
/0/N+5lY1jXmVsEAXwYU4uu/8HyMlOtrPNtylXYVsvrpAeotunrXG75sVjsK5S/d3uX5VU73HL7K06UsdqQLqDKvDiUIYFuSdwHL
VvoeC7+fnsbVb/jZQVUAS1+uXr9kKO1N+w3EBtrZaRZStZKYPQ8/ZNpbTX3+885Kdr87+nHpg6LvVanKtzstTYsMtYMzpzCbY+rr
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
H8dXr+CKWUGpsI5v3/4LTSP9gw==""")).decode("utf-8"))

CONSTRAINT_TYPES = ["IsoBallJoint_0", "IsoBallJoint_1", "IsoBallJoint_2", "AnisoBallJoint_0", "AnisoBallJoint_1",
                    "AnisoBallJoint_2", "IsoPlungeJoint", "Bar_0", "Bar_1", "Bar_2", "Lever_2", "Lever_3", "PureHinge",
                    "AngularHinge", "IsoOriJoint_0", "IsoOriJoint_1", "AnisoOriJoint_0", "AnisoOriJoint_1", "ConeTwist",
                    "RotJoint", "RotJoint_X", "RotJoint_Z", "Gearbox", "Gearbox_Z", "Differential", "Differential_ZX"]
TIRE_LOCATIONS = ["NONE", "FRONTLEFT", "FRONTRIGHT", "REARLEFT", "REARRIGHT", "FRONT", "REAR", "LEFT", "RIGHT", "ALL"]


def log(msg=""):
    print(msg, flush=True)


# ===========================================================================
#  UE5-Paket lesen
# ===========================================================================
class Reader:
    def __init__(self, b, p=0):
        self.b, self.p = b, p

    def read(self, n):
        v = self.b[self.p:self.p + n]
        self.p += n
        return v

    def u8(self):
        v = self.b[self.p]
        self.p += 1
        return v

    def u16(self):
        v = struct.unpack_from("<H", self.b, self.p)[0]
        self.p += 2
        return v

    def i32(self):
        v = struct.unpack_from("<i", self.b, self.p)[0]
        self.p += 4
        return v

    def u32(self):
        v = struct.unpack_from("<I", self.b, self.p)[0]
        self.p += 4
        return v

    def i64(self):
        v = struct.unpack_from("<q", self.b, self.p)[0]
        self.p += 8
        return v

    def f32(self):
        v = struct.unpack_from("<f", self.b, self.p)[0]
        self.p += 4
        return v

    def f64(self):
        v = struct.unpack_from("<d", self.b, self.p)[0]
        self.p += 8
        return v

    def fstr(self):
        n = self.i32()
        if n == 0:
            return ""
        if n > 0:
            v = self.b[self.p:self.p + n - 1].decode("utf-8", "replace")
            self.p += n
            return v
        v = self.b[self.p:self.p - n * 2 - 2].decode("utf-16-le", "replace")
        self.p += -n * 2
        return v


class Package:
    def __init__(self, base):
        self.base = base
        self.name = os.path.basename(base)
        with open(base + ".uasset", "rb") as fh:
            b = fh.read()
        r = Reader(b)
        r.u32()
        legacy = r.i32()
        if legacy != -4:
            r.i32()
        r.i32()
        if legacy <= -8:
            r.i32()
        r.i32()
        cv = r.i32()
        r.p += 20 * cv
        self.header_size = r.i32()
        r.fstr()
        r.u32()
        nc, no = r.i32(), r.i32()
        r.i32(); r.i32(); r.i32(); r.i32()
        ec, eo, ic, io, dep = (r.i32() for _ in range(5))
        r.p = no
        self.names = []
        for _ in range(nc):
            self.names.append(r.fstr())
            r.p += 4
        r.p = io
        self.imports = []
        for _ in range(ic):
            r.p += 8
            cls = self._fname(r)
            outer = r.i32()
            obj = self._fname(r)
            r.p += 4
            self.imports.append((cls, outer, obj))
        esize = (dep - eo) // ec if ec else 0
        self.exports = []
        for k in range(ec):
            r.p = eo + k * esize
            ci = r.i32(); r.i32(); r.i32(); r.i32()
            nm = self._fname(r)
            r.u32()
            size = r.i64()
            off = r.i64()
            self.exports.append({"cls": ci, "name": nm, "size": size, "off": off})

    def _fname(self, r):
        i, n = r.i32(), r.i32()
        s = self.names[i] if 0 <= i < len(self.names) else "?"
        return s if n == 0 else "%s_%d" % (s, n - 1)

    def ref(self, idx):
        if idx < 0 and -idx - 1 < len(self.imports):
            cls, outer, obj = self.imports[-idx - 1]
            path = None
            o = idx
            while o < 0:
                c, ou, ob = self.imports[-o - 1]
                if ou == 0:
                    path = ob
                    break
                o = ou
            return {"name": obj, "class": cls, "path": path}
        if idx > 0 and idx - 1 < len(self.exports):
            return {"name": self.exports[idx - 1]["name"], "class": None, "path": None}
        return None

    def main_export(self, want=None):
        with open(self.base + ".uexp", "rb") as fh:
            u = fh.read()
        pick = self.exports[0]
        for e in self.exports:
            c = self.ref(e["cls"])
            if want and c and c["name"] == want:
                pick = e
                break
        cls = (self.ref(pick["cls"]) or {}).get("name")
        s = pick["off"] - self.header_size
        return cls, u[s:s + pick["size"]]


# ===========================================================================
#  Unversioned-Properties dekodieren (mit eingebettetem Schema)
# ===========================================================================
def _flatten(props):
    out = []
    for p in props:
        out += [p] * max(1, p.get("dim", 1))
    return out


_slot_cache = {}


def struct_slots(sname):
    if sname in _slot_cache:
        return _slot_cache[sname]
    st = SCHEMA["structs"].get(sname)
    if st is None:
        return None
    sup = struct_slots(st["super"]) if st["super"] else []
    res = _flatten(st["props"]) + (sup or [])     # eigene Properties vor denen der Basis
    _slot_cache[sname] = res
    return res


class Decoder:
    def __init__(self, pkg):
        self.pkg = pkg

    def header(self, r):
        frags = []
        while True:
            v = r.u16()
            frags.append((v & 0x7F, (v >> 7) & 1, v >> 9))
            if (v >> 8) & 1:
                break
        nz = sum(n for s, z, n in frags if z)
        mask = []
        if nz:
            if nz <= 8:
                bits = r.u8()
            elif nz <= 16:
                bits = r.u16()
            else:
                bits = 0
                for k in range((nz + 31) // 32):
                    bits |= r.u32() << (32 * k)
            mask = [(bits >> k) & 1 for k in range(nz)]
        return frags, mask

    def props(self, r, slots):
        frags, mask = self.header(r)
        out = {}
        idx = zi = 0
        for skip, zero, num in frags:
            idx += skip
            for _ in range(num):
                p = slots[idx]
                idx += 1
                if zero:
                    z = mask[zi]
                    zi += 1
                    if z:
                        continue
                v = self.value(r, p)
                if p.get("dim", 1) > 1:
                    out.setdefault(p["name"], []).append(v)
                else:
                    out[p["name"]] = v
        return out

    def struct(self, r, sname):
        if sname == "KeyHandleMap":
            return None
        if sname == "RichCurveKey":
            im = r.u8(); r.u8(); r.u8()
            t, v, at, atw, lt, ltw = struct.unpack_from("<6f", r.b, r.p)
            r.p += 24
            return {"Time": t, "Value": v, "Interp": im, "Arrive": at, "Leave": lt}
        if sname in ("Vector", "Rotator"):
            v = struct.unpack_from("<3d", r.b, r.p); r.p += 24; return list(v)
        if sname == "Vector2D":
            v = struct.unpack_from("<2d", r.b, r.p); r.p += 16; return list(v)
        if sname in ("Vector4", "Quat"):
            v = struct.unpack_from("<4d", r.b, r.p); r.p += 32; return list(v)
        if sname == "IntPoint":
            v = struct.unpack_from("<2i", r.b, r.p); r.p += 8; return list(v)
        if sname == "Color":
            v = list(r.read(4)); return v
        if sname == "Guid":
            r.p += 16; return None
        if sname == "LinearColor":
            v = struct.unpack_from("<4f", r.b, r.p); r.p += 16; return list(v)
        slots = struct_slots(sname)
        if slots is None:
            raise ValueError("Struct %s fehlt im Schema" % sname)
        return self.props(r, slots)

    def name(self, r):
        i, n = r.i32(), r.i32()
        nm = self.pkg.names[i] if 0 <= i < len(self.pkg.names) else "?"
        return nm if n == 0 else "%s_%d" % (nm, n - 1)

    def value(self, r, p, inner=False):
        t = p["type"]
        if t == "Str":
            return r.fstr()
        if t == "Struct":
            return self.struct(r, p["struct"])
        if t == "Int":
            return r.i32()
        if t == "UInt32":
            return r.u32()
        if t == "Int64":
            return r.i64()
        if t == "Float":
            return r.f32()
        if t == "Double":
            return r.f64()
        if t == "Bool":
            return bool(r.u8())
        if t in ("Byte", "Int8"):
            return r.u8()
        if t == "Enum":
            if inner:
                return self.name(r).split("::")[-1]
            return self.value(r, p["underlying"])
        if t == "Name":
            return self.name(r)
        if t in ("Object", "Class", "Interface"):
            return self.pkg.ref(r.i32())
        if t in ("SoftObject", "SoftClass"):
            a = self.name(r); b = self.name(r); r.fstr()
            return {"name": b, "path": a}
        if t in ("Array", "Set"):
            if t == "Set":
                r.i32()
            return [self.value(r, p["inner"], True) for _ in range(r.i32())]
        if t == "Map":
            r.i32()
            return [[self.value(r, p["key"], True), self.value(r, p["value"], True)] for _ in range(r.i32())]
        if t == "Text":
            r.u32()
            ht = struct.unpack("<b", bytes([r.u8()]))[0]
            if ht == -1:
                return r.fstr() if r.i32() else ""
            if ht == 0:
                r.fstr(); r.fstr(); return r.fstr()
            if ht == 11:
                tid = self.name(r); key = r.fstr()
                return {"table": tid, "key": key}
            raise ValueError("FText-Typ %d" % ht)
        raise ValueError("Typ %s nicht unterstuetzt" % t)


def decode(base, cls=None):
    pkg = Package(base)
    c, data = pkg.main_export(cls)
    cls = cls or c
    if cls not in SCHEMA["classes"]:
        raise ValueError("Klasse %s nicht im Schema" % cls)
    slots = _flatten(SCHEMA["classes"][cls])
    best = None
    for start in (0, 4):
        try:
            r = Reader(data, start)
            out = Decoder(pkg).props(r, slots)
        except Exception as ex:      # noqa
            best = best or ex
            continue
        if len(data) - r.p <= 8:     # komplett gelesen (Rest = Footer)
            return out, pkg
        best = out if not isinstance(best, dict) else best
    if isinstance(best, dict):
        return best, pkg
    raise best


# ===========================================================================
#  Rennsport-Werte -> rF2-Text
# ===========================================================================
def V(x):
    """ValueAsString / ValueAsStringVectorN -> String bzw. Liste; leer -> None"""
    if x is None:
        return None
    if isinstance(x, str):
        return x if x != "" else None
    if isinstance(x, dict):
        if set(x) <= {"Value"}:
            v = x.get("Value")
            return v if v not in (None, "") else None
        if set(x) <= {"X", "Y", "Z", "W"}:
            comps = [(V(x.get(k)) or "") for k in ("X", "Y", "Z", "W") if k in SCHEMA_VEC_KEYS(x)]
            return comps if any(c != "" for c in comps) else None
    if isinstance(x, bool):
        return "1" if x else "0"
    if isinstance(x, (int, float)):
        return fmt_num(x)
    return None


def SCHEMA_VEC_KEYS(x):
    keys = [k for k in ("X", "Y", "Z", "W") if k in x]
    # fehlende (leere) Komponenten auffuellen, damit die Stelligkeit stimmt
    n = {"X": 1, "Y": 2, "Z": 3, "W": 4}[keys[-1]] if keys else 0
    return ("X", "Y", "Z", "W")[:n]


def fmt_num(x):
    if isinstance(x, float):
        s = ("%.7g" % x)
        return s
    return str(x)


def text(v):
    if v is None:
        return None
    if isinstance(v, list):
        return "(" + ",".join(v) + ")"
    return v


class Ini:
    def __init__(self):
        self.lines = []

    def section(self, name):
        if self.lines and self.lines[-1] != "":
            self.lines.append("")
        self.lines.append("[%s]" % name)

    def kv(self, key, value):
        t = text(value)
        if t is not None:
            self.lines.append("%s=%s" % (key, t))

    def raw(self, line):
        self.lines.append(line)

    def comment(self, line):
        self.lines.append("// " + line)

    def mod(self, prefix, m):
        """VehicleModificationData -> <prefix>Range / Setting / Special / Caption"""
        if not isinstance(m, dict):
            return
        cap = m.get("Caption")
        if cap:
            self.lines.append('%sCaption="%s"' % (prefix, cap))
        self.kv(prefix + "Range", V(m.get("Range")))
        self.kv(prefix + "Setting", V(m.get("Setting")))
        for sp in m.get("Special") or []:
            c = V(sp) or []
            c = list(c) + [""] * (4 - len(c))
            x, y, z, w = c[:4]
            yq = '"%s"' % y if y != "" else ""
            zq = '"%s"' % z if z != "" else ""
            self.lines.append("%sSpecial=(%s,%s,%s,%s)" % (prefix, x, yq, zq, w))

    def text(self):
        return "\n".join(self.lines) + "\n"


def write_struct(ini, data, rename=None, prefix="", skip=(), order=None):
    """Generisch: alle Properties eines Structs schreiben (Umbenennung + Prefix)."""
    rename = rename or {}
    keys = order or list(data.keys())
    for k in keys:
        if k not in data or k in skip:
            continue
        v = data[k]
        key = rename.get(k)
        if key is None:
            key = prefix + (k[1:] if re.match(r"^b[A-Z]", k) else k)
        if isinstance(v, dict) and ("Range" in v or "Setting" in v or "Special" in v):
            ini.mod(key, v)
        elif isinstance(v, list):
            vals = [V(x) for x in v]
            vals = [x for x in vals if x is not None]
            if not vals:
                continue
            if all(isinstance(x, str) for x in vals) and len(vals) > 1 and k in ("WearGrip",):
                ini.kv(key, "(" + ",".join(vals) + ")")
            else:
                for x in vals:
                    ini.kv(key, x)
        elif isinstance(v, dict) and set(v) <= {"name", "class", "path"}:
            continue
        else:
            ini.kv(key, V(v))


def short(x):
    return x["name"] if isinstance(x, dict) else x


# ---------------------------------------------------------------------------
#  HDV
# ---------------------------------------------------------------------------
GENERAL_RENAME = {
    "GarageRules": "Rules", "FuelTankForceDistribution": "FuelTankForceDistrib", "bSymmetric": "Symmetric",
    "CenterOfGravityHeightClassic": "CGHeight", "CenterOfGravityHeight": "CGHeight",
    "CenterOfGravityRight": "CGRight", "CenterOfGravityRear": "CGRear",
    "AIFuelMultiplier": "AIFuelMult", "AIPerformanceUsage": "AIPerfUsage",
}
AERO_COMMON = {"DraftLiftMultiplier": "DraftLiftMult", "ForceDistribution": "ForceDistrib"}


PITMENU_DEFAULT = ["StopGo=1", "Fuel=1", "AllTires=1", "FrontRearTires=(1,1)", "LeftRightTires=(0,0)",
                   "IndividualTires=(0,0,0,0)", "FenderFlare=(0,0)", "FrontWing=0", "RearWing=0", "Driver=1",
                   "Wedge=0", "Radiator=0", "TrackBar=0", "Pressure=(1,1,1,1)", "SpringRubber=(0,0,0,0)",
                   "Damage=1", "StopGoSimultaneous=0", "PressureOnTheFly=1", "DamagedTiresOnly=0",
                   "CompoundRestrictions=2", "Preparation=(140,17,0.3,5)", "FuelTime=(0.8,2.2,1.4,0.9,0)",
                   "TireTime=(3.5,3.5,1.8,1)", "FenderFlareTime=0", "FrontWingTime=(4.5,11.5)",
                   "RearWingTime=(50,50)", "DriverTime=(32,4.8,3.9,0)", "WedgeTime=0", "RadiatorTime=50",
                   "TrackBarTime=0", "PressureTime=4", "SpringRubberTime=0", "DamageTime=(12,10,150,1)"]


RENNSPORT_ONLY_DRIVELINE = ("HybridGearRatio", "bElectricMotorBumpStartAvailable",
                            "MotorGeneratorUnitKineticDeliveryMode", "MotorGeneratorUnitKineticRecoveryMode",
                            "MotorGeneratorUnitKineticDeliveryModeSpeedThreshold",
                            "MotorGeneratorUnitKineticDeliveryModeTexts",
                            "MotorGeneratorUnitKineticDeliveryModeMappings")


MOTOR_HANDLED = ("HybridGearRatio", "MotorGeneratorUnitKineticDeliveryMode", "MotorGeneratorUnitKineticRecoveryMode",
                 "MotorGeneratorUnitKineticDeliveryModeTexts")


def _short_val(v):
    if isinstance(v, dict) and ("Range" in v or "Setting" in v):
        return "Range=%s Setting=%s" % (text(V(v.get("Range"))), V(v.get("Setting")))
    if isinstance(v, list):
        parts = []
        for x in v:
            if isinstance(x, dict) and "key" in x:
                parts.append(x["key"])
            elif isinstance(x, dict):
                parts.append("/".join("%s:%s" % kv for kv in x.items()) or "-")
            else:
                parts.append(str(V(x)))
        return ", ".join(parts)
    s = V(v)
    return text(s) if s is not None else None


def write_hdv(phys, car, files):
    ini = Ini()
    ini.raw("// %s - konvertiert aus Rennsport (rennsport_rf2.py)" % car)

    g = phys.get("General", {})
    ini.section("GENERAL")
    write_struct(ini, g, GENERAL_RENAME, skip=("Undertray", "TireBrandData", "FLUndertray", "FRUndertray",
                                               "RLUndertray", "RRUndertray", "UndertrayParams",
                                               "BatteryChargeWithSOCCurve", "BatteryDischargeWithSOCCurve",
                                               "BatteryChargeWithRPMCurve", "BatteryDischargeWithRPMCurve",
                                               "VehicleType", "FrontTireCompound", "RearTireCompound", "Fuel"))
    for i, u in enumerate(g.get("Undertray") or []):
        ini.kv("Undertray%02d" % i, V(u))
    ini.kv("UndertrayParams", V(g.get("UndertrayParams")))
    if files.get("tbc"):
        ini.raw('TireBrand="%s"' % files["tbc"])
    ini.mod("FrontTireCompound", g.get("FrontTireCompound"))
    ini.mod("RearTireCompound", g.get("RearTireCompound"))
    ini.mod("Fuel", g.get("Fuel"))
    vt = g.get("VehicleType")
    if vt:
        ini.comment("Rennsport VehicleType=%s (%s)" % (vt, {1: "Elektro", 2: "Hybrid"}.get(vt, "?")))
    for k in ("BatteryChargeWithSOCCurve", "BatteryDischargeWithSOCCurve",
              "BatteryChargeWithRPMCurve", "BatteryDischargeWithRPMCurve"):
        c = (files.get("curves") or {}).get(k)
        if c:
            ini.comment("Rennsport %s (kein rF2-Gegenstueck): %s" % (k, c))

    # Rennsport hat keine Boxenstopp-/Plugin-Daten -> rF2-Standardwerte
    ini.section("PITMENU")
    ini.comment("Standardwerte (nicht in Rennsport enthalten)")
    for line in PITMENU_DEFAULT:
        ini.raw(line)
    ini.section("PLUGIN")
    for line in ("AerodynamicSensor=0", "EngineSensor=0", "SuspensionSensor=1", "TireForceSensor=0",
                 "TireTemperatureSensor=1"):
        ini.raw(line)

    ap = phys.get("AidPenalties")
    if ap:
        ini.section("AIDPENALTIES")
        write_struct(ini, ap, {"AutoShift": "Autoshift", "OppositeLock": "Opposite"})

    fw = phys.get("FrontWing")
    if fw:
        ini.section("FRONTWING")
        ini.kv("FWForceDistrib", V(fw.get("ForceDistribution")))
        ini.mod("FW", fw.get("WingModificationData"))
        write_struct(ini, fw, {k: "FW" + v for k, v in AERO_COMMON.items()}, prefix="FW",
                     skip=("WingModificationData", "ForceDistribution"))
    rw = phys.get("RearWing")
    if rw:
        ini.section("REARWING")
        ini.kv("RWForceDistrib", V(rw.get("ForceDistribution")))
        ini.mod("RW", rw.get("WingModificationData"))
        write_struct(ini, rw, {k: "RW" + v for k, v in AERO_COMMON.items()}, prefix="RW",
                     skip=("WingModificationData", "ForceDistribution"))
    for sec, key in (("LEFTFENDER", "LeftFender"), ("RIGHTFENDER", "RightFender")):
        f = phys.get(key)
        if f:
            ini.section(sec)
            ini.kv("FenderForceDistrib", V(f.get("ForceDistribution")))
            ini.mod("Fender", f.get("ModificationData"))
            write_struct(ini, f, {k: "Fender" + v for k, v in AERO_COMMON.items()}, prefix="Fender",
                         skip=("ModificationData", "ForceDistribution"))
    b = phys.get("BodyAero")
    if b:
        ini.section("BODYAERO")
        ini.kv("BodyForceDistrib", V(b.get("ForceDistribution")))
        body_prefixed = ("DragBase", "DragHeightAvg", "DragHeightDiff", "MaxHeight", "NegRakeDrag", "PosRakeDrag",
                         "NegRakeLift", "PosRakeLift", "Left", "Right", "Up", "Down", "Aft", "Fore", "Rot", "Center")
        ren = {k: "Body" + k for k in body_prefixed}
        ren.update({"DraftLiftMultiplier": "BodyDraftLiftMult", "DraftBalanceMultiplier": "DraftBalanceMult",
                    "RoadModifierMultipliers": "RoadModifierMults"})
        write_struct(ini, b, ren, skip=("ForceDistribution",))
    df = phys.get("Diffuser")
    if df:
        ini.section("DIFFUSER")
        ini.kv("DiffuserForceDistrib", V(df.get("ForceDistribution")))
        write_struct(ini, df, {"DraftLiftMultiplier": "DiffuserDraftLiftMult"}, prefix="Diffuser",
                     skip=("ForceDistribution",))

    s = phys.get("Suspension", {})
    ini.section("SUSPENSION")
    if files.get("chassis"):
        ini.raw("UltraChassis=%s" % files["chassis"])
    write_struct(ini, s, {"CorrectedInnerSuspensionHeightAll": "CorrectedInnerSuspHeightAll",
                          "bAdjustSuspensionRates": "AdjustSuspRates"}, skip=("Chassis",))

    c = phys.get("Controls", {})
    ini.section("CONTROLS")
    write_struct(ini, c, {"Handfrontbrake4WDRelease": "Handfrontbrake4WDRelease"})

    ini.section("ENGINE")
    if files.get("motor") and not files.get("motor_linked"):
        ini.raw("Normal=%s" % files["motor"])          # Elektroauto: Motor-INI ist der Antrieb
    elif files.get("engine"):
        ini.raw("Normal=%s" % files["engine"])
    for k, v in (files.get("engine_mults") or {}).items():
        ini.kv(k, v)
    if files.get("motor") and files.get("motor_linked"):
        ini.section("ELECTRIC_BOOST_MOTOR")
        ini.raw("Normal=%s" % files["motor"])

    d = phys.get("Driveline", {})
    ini.section("DRIVELINE")
    write_struct(ini, d, {"EngineTorqueDistribution": "EngineTorqueDistrib",
                          "ClutchTorqueDistribution": "ClutchTorqueDistrib",
                          "DifferentialTorqueDistribution": "DifferentialTorqueDistrib",
                          "GearboxTorqueDistribution": "GearboxTorqueDistrib"},
                 skip=("Gears", "MaximumCombinedTorqueCurve") + RENNSPORT_ONLY_DRIVELINE)
    for line in files.get("gear_lines") or []:
        ini.raw(line)
    if files.get("combined_torque"):
        ini.comment("Rennsport MaximumCombinedTorqueCurve (Verbrenner+E-Motor, rpm,Nm): " + files["combined_torque"])
    extra = []
    for k in RENNSPORT_ONLY_DRIVELINE:
        v = d.get(k)
        if v in (None, "", [], {}) or (files.get("motor") and k in MOTOR_HANDLED):
            continue
        s = _short_val(v)
        if s:
            extra.append("%s=%s" % (k, s))
    if extra:
        ini.comment("Rennsport-Hybrid/Elektro (kein rF2-Gegenstueck):")
        for e in extra:
            ini.comment("  " + e)

    for sec, key in (("FRONTLEFT", "FrontLeftWheel"), ("FRONTRIGHT", "FrontRightWheel"),
                     ("REARLEFT", "RearLeftWheel"), ("REARRIGHT", "RearRightWheel")):
        w = phys.get(key)
        if not w:
            continue
        ini.section(sec)
        write_struct(ini, w, {"BumpstopTravels": "BumpStopTravels",
                              "PushrodOutboardForceDistribution": "PushrodOutboard",
                              "PushrodInboardForceDistribution": "PushrodInboard"})
    bop = phys.get("BalanceOfPerformanceData")
    if bop:
        ini.raw("")
        ini.comment("Rennsport Balance of Performance (nicht Teil von rF2): " +
                    ", ".join("%s=%s" % (k, fmt_num(v) if isinstance(v, (int, float)) else short(v))
                              for k, v in bop.items()))
    return ini.text()


# ---------------------------------------------------------------------------
#  Elektromotor (Hybrid / Elektro)
# ---------------------------------------------------------------------------
def load_curve(content, ref):
    """UCurveFloat -> sortierte Keys"""
    if not isinstance(ref, dict) or not ref.get("path"):
        return None
    b = game_path(content, ref["path"])
    if not b or not os.path.isfile(b + ".uasset"):
        log("  [!] nicht gefunden: %s" % ref["path"])
        return None
    d, _ = decode(b, "CurveFloat")
    keys = (d.get("FloatCurve") or {}).get("Keys") or []
    return sorted((k for k in keys if isinstance(k, dict)), key=lambda k: k["Time"])


def curve_points(keys, step=None, xmax=None):
    """Stuetzstellen: Keys + (bei kubischen Abschnitten) Zwischenpunkte"""
    if not keys:
        return []
    xs = {k["Time"] for k in keys}
    if step:
        x = keys[0]["Time"]
        end = max(keys[-1]["Time"], xmax or 0)
        while x <= end + 1e-6:
            xs.add(round(x, 6))
            x += step
    return [(x, curve_eval(keys, x)) for x in sorted(xs)]


def curve_text(keys):
    return " ".join("(%s,%s)" % (fmt_num(float(k["Time"])), fmt_num(float(k["Value"]))) for k in keys or [])


MOTOR_ENGINE_KEYS = ("OilTemps", "CombustionHeat", "EngineSpeedHeat", "OilMinimumCooling", "OilWaterHeatTransfer",
                     "WaterMinimumCooling", "RadiatorCooling", "LifetimeEngineRPM", "LifetimeOilTemp", "LifetimeAvg",
                     "LifetimeVar", "EngineEmission", "EngineSound", "SpeedLimiter", "FuelEstimate")


def write_motor(content, mot, car, phys, engine_text=None, strings=None):
    """Rennsport ElectricMotorData -> rF2-Motordatei (EngineType=2, Format wie FE Gen3 / GR010)"""
    g = mot.get("GlobalData") or {}
    dl = phys.get("Driveline") or {}
    ini = Ini()
    ini.raw("// %s - Elektromotor (konvertiert aus Rennsport)" % car)
    ini.raw("EngineType=2")
    ini.raw("MotorGearRatio=%s" % (V(dl.get("HybridGearRatio")) or "1"))
    ini.kv("MotorInertia", V(g.get("Inertia")))
    vmax = _num(V(g.get("MaximumRPM")))
    eff = _num(V(g.get("Efficiency")))
    tq = load_curve(content, g.get("TorqueCurve"))
    bt = load_curve(content, g.get("BrakeTorqueCurve"))
    pmax = 0.0
    pts = curve_points(tq, 250.0, vmax)
    pts = [(x, y) for x, y in pts if not vmax or x <= vmax]
    for x, y in pts:
        ini.raw("ThrottleTorque=(%s,0,%s)" % (fmt_num(float(x)), fmt_num(float(y))))
        pmax = max(pmax, y * x * 2 * 3.141592653589793 / 60.0)
    if pts:
        ini.raw("ThrottleTorque=(%s,0,0)" % fmt_num(float(pts[-1][0] + 1000)))
    bpts = curve_points(bt, 250.0, vmax)
    bpts = [(x, y) for x, y in bpts if not vmax or x <= vmax]
    for x, y in bpts:
        ini.raw("RegenerationTorque=(%s,0,%s)" % (fmt_num(float(x)), fmt_num(float(y))))
    if bpts:
        ini.raw("RegenerationTorque=(%s,0,0)" % fmt_num(float(bpts[-1][0] + 1000)))
    if eff:
        ini.raw("Efficiency=(0,%s)" % fmt_num(eff))
        ini.raw("Efficiency=(%s,%s)" % (fmt_num(vmax or 20000.0), fmt_num(eff)))
    if pmax:
        e = pmax / (eff or 1.0)
        ini.raw("FullThrottleEnergyConsumption=%s" % fmt_num(round(e)))
        ini.raw("MaxEnergyConsumption=%s" % fmt_num(round(e)))
    if _num(V(g.get("RequireBrakeToRegen")), 0):
        ini.raw("CoastingRegeneration=0")
        ini.raw("BrakingRegeneration=1")
    elif bpts:
        ini.raw("CoastingRegeneration=1")
        ini.raw("BrakingRegeneration=1")
    # Rennsport MGU-K-Modi -> rF2-Karten
    dm = dl.get("MotorGeneratorUnitKineticDeliveryMode")
    if isinstance(dm, dict) and V(dm.get("Range")):
        ini.mod("ElectricMotorMap", dm)
        texts = dl.get("MotorGeneratorUnitKineticDeliveryModeTexts") or []
        names = [(strings or {}).get(x.get("key"), x.get("key")) for x in texts if isinstance(x, dict)]
        rng = V(dm.get("Range")) or []
        n = int(_num(rng[2], 0)) if len(rng) > 2 else 0
        if names and n and len(names) == n:
            for i, nm in enumerate(names):
                ini.raw('ElectricMotorMapSpecial=(%d,"%s",,)' % (i, nm))
    rm = dl.get("MotorGeneratorUnitKineticRecoveryMode")
    if isinstance(rm, dict) and V(rm.get("Range")):
        rm = json.loads(json.dumps(rm))
        rz = (rm.get("Range") or {}).get("Z") or {}
        if _num(rz.get("Value"), 0) < 1:           # rF2 braucht mindestens 1 Stufe
            rm["Range"]["Z"] = {"Value": "1"}
        ini.mod("RegenerationMap", rm)
    if vmax:
        ini.raw("RevLimitRange=(%s,0,1)" % fmt_num(vmax))
    ini.kv("WheelDrive", V(dl.get("WheelDrive")))
    if engine_text:      # Elektroauto: Waerme/Lebensdauer/Sound aus der Rennsport-EngineData
        for line in engine_text.splitlines():
            if line.split("=")[0] in MOTOR_ENGINE_KEYS:
                ini.raw(line)
    for k in ("PeakTorqueMultiplier", "PeakTorqueTimes", "RegenerationEfficiency", "RequireBrakeToRegen"):
        s = text(V(g.get(k)))
        if s:
            ini.comment("Rennsport %s=%s (kein rF2-Gegenstueck)" % (k, s))
    return ini.text()


# ---------------------------------------------------------------------------
#  Chassis.ini
# ---------------------------------------------------------------------------
def write_chassis(ch, car):
    ini = Ini()
    ini.raw("// %s - Chassis (konvertiert aus Rennsport)" % car)
    for rb in ch.get("RigidBodies") or []:
        ini.section("RigidBody")
        ini.raw('Name="%s"' % rb.get("Name", ""))
        write_struct(ini, rb, skip=("Name",))
    for cn in ch.get("Constraints") or []:
        ini.section("Constraint")
        t = cn.get("Type", 0)
        ini.raw("Type=%s" % (CONSTRAINT_TYPES[t] if isinstance(t, int) and t < len(CONSTRAINT_TYPES) else t))
        for k in ("Name", "BodyA", "BodyB", "BodyC", "BodyD"):
            if cn.get(k):
                ini.raw('%s="%s"' % (k, cn[k]))
        write_struct(ini, cn, skip=("Type", "Name", "BodyA", "BodyB", "BodyC", "BodyD"))
    return ini.text()


# ---------------------------------------------------------------------------
#  Engine.ini
# ---------------------------------------------------------------------------
def pair(*vals):
    vals = [V(v) for v in vals]
    if all(v is None for v in vals):
        return None
    return "(" + ",".join(v or "" for v in vals) + ")"


def write_engine(eng, car):
    ini = Ini()
    ini.raw("// %s - Engine (konvertiert aus Rennsport)" % car)
    g = eng.get("GlobalData", {})
    ini.kv("ReferenceConditions", pair(g.get("ICEReferencePressure"), g.get("ICEReferenceDensity"),
                                       g.get("ICEReferenceMixture")))
    for pt in g.get("EngineCurve") or []:
        vals = [fmt_num(pt.get(k) or 0.0) for k in ("RPMBase", "FrictionalTorque", "MaxTorque",
                                                    "ICEIdleFunction", "ICEPressurePower")]
        ini.raw("RPMBase=(%s)" % ",".join(vals))
        vf = pt.get("ICEAccelVolumeFract")
        if vf:
            ini.raw("VolumeFract=(%s)" % ",".join(fmt_num(x or 0.0) for x in vf))
        mf = pt.get("ICEAccelMixtureFract")
        if mf:
            ini.raw("MixtureFract=(%s)" % ",".join(fmt_num(x or 0.0) for x in mf))
    ini.kv("FuelAirMixtureTable", pair(g.get("FuelAirMixtureTableStart"), g.get("FuelAirMixtureTableStep")))
    for e in g.get("FuelAirMixtureEffects") or []:
        ini.kv("FuelAirMixtureEffects", pair(e.get("TempTorqueMultiplier"), e.get("ExhaustGasTempMultiplier")))
    for k in ("FuelConsumption", "FuelEstimate", "FuelDensity", "EngineInertia"):
        ini.kv(k, V(g.get(k)))
    ini.kv("IdleRPMLogic", pair(g.get("IdleRPMMin"), g.get("IdleRPMMax")))
    ini.kv("LaunchEfficiency", V(g.get("LaunchEfficiency")))
    ini.kv("LaunchRPMLogic", pair(g.get("LaunchRPMMin"), g.get("LaunchRPMMax")))
    ini.kv("LaunchVariables", V(g.get("LaunchVariables")))
    ga = eng.get("Garage", {})
    ini.mod("RevLimit", ga.get("RevLimitRPM"))
    ini.kv("RevLimitAvailable", V(g.get("bRevLimitAvailable")))
    ini.kv("RevLimitLogic", V(g.get("RevLogicRPM")))
    ini.kv("RevLimitHardTime", V(g.get("RevLimitHardTime")))
    ini.mod("EngineMixture", ga.get("EngineMixture"))
    ini.mod("EngineBrakingMap", ga.get("EngineBrakingMap"))
    eb = eng.get("EngineBraking") or {}
    if eb:
        ini.kv("EngineBrakingParams", "(%s,%s)" % (eb.get("Type", 0), V(eb.get("StepRPM")) or "0"))
        # rF2: EngineBrakingLimit gilt fuer alle Gaenge, danach EngineBrakingGear0..9Limit (0 = Rueckwaerts)
        lim = (eb.get("GlobalBrakingLimits") or {}).get("LimitValues")
        if lim:
            ini.raw("EngineBrakingLimit=(%s)" % ",".join(fmt_num(x or 0.0) for x in lim))
        lim = (eb.get("ReverseGearBrakingLimits") or {}).get("LimitValues")
        if lim:
            ini.raw("EngineBrakingGear0Limit=(%s)" % ",".join(fmt_num(x or 0.0) for x in lim))
        for i, gl in enumerate(eb.get("ForwardGearBrakingLimits") or []):
            lv = (gl or {}).get("LimitValues")
            if lv:
                ini.raw("EngineBrakingGear%dLimit=(%s)" % (i + 1, ",".join(fmt_num(x or 0.0) for x in lv)))

    ini.mod("EngineBoost", ga.get("EngineBoost"))
    bo = eng.get("Boost") or {}
    ini.kv("BoostEffects", pair(bo.get("AdditionalRPM"), bo.get("Fuel"), bo.get("Wear")))
    ini.kv("OilTemps", pair(g.get("OilStartFract"), g.get("OilOptimumCelsius")))
    for k in ("CombustionHeat", "EngineSpeedHeat", "OilMinimumCooling"):
        ini.kv(k, V(g.get(k)))
    ini.kv("OilWaterHeatTransfer", pair(g.get("OilWaterHeatTransferMin"), g.get("OilWaterHeatTransferPerRPS")))
    ini.kv("WaterMinimumCooling", V(g.get("WaterMinimumCooling")))
    ini.kv("RadiatorCooling", pair(g.get("RadiatorCoolingBase"), g.get("RadiatorCoolingIncrement")))
    ini.kv("LifetimeEngineRPM", V(g.get("LifetimeRPM")))
    ini.kv("LifetimeOilTemp", V(g.get("LifetimeOilTempCelsius")))
    ini.kv("LifetimeAvg", V(g.get("LifetimeAvg")))
    ini.kv("LifetimeVar", V(g.get("LifetimeVar")))
    ini.kv("EngineEmission", V(g.get("Placeholder_ExhaustEmissionPos")))
    ini.kv("EngineSound", V(g.get("Placeholder_EngineSoundPos")))
    ini.kv("SpeedLimiter", V(g.get("bSpeedLimiterAvailable")))
    ini.kv("OnboardStarter", V(g.get("bOnboardStarterAvailable")))
    ini.kv("StarterTiming", V(g.get("StarterTimer")))
    ram = eng.get("Ram") or {}
    ini.kv("RamCenter", V(ram.get("Center")))
    ini.kv("RamDraftMult", V(ram.get("DraftMultiplier")))
    ini.kv("RamPressure", pair(ram.get("SpeedToPressureMult1"), ram.get("SpeedToPressureMult2")))
    for t in eng.get("Turbines") or []:
        ini.kv("TurboInertia", V(t.get("Inertia")))
        ini.kv("TurboFriction", pair(t.get("FrictionTorque"), t.get("FrictionPower")))
        ini.kv("TurboStaticFrictionWatts", V(t.get("StaticFrictionWatts")))
        ini.kv("TurbineFlowTable", pair(t.get("FlowStart"), t.get("FlowStep")))
        for f in t.get("FlowData") or []:
            ini.kv("TurbineFlowEffects", pair(f.get("PressureRatio"), f.get("Efficiency")))
        cd = t.get("CompressorData") or {}
        if cd:
            ini.kv("CompressorTable", pair(cd.get("SpeedStep"), cd.get("FlowStep")))
            for fl in cd.get("FlowData") or []:
                re_ = fl.get("RatioEfficiencies") or []
                ini.raw("CompressorPressRatio=(%s)" % ",".join(V(x.get("PressureRatio")) or "" for x in re_))
                ini.raw("CompressorEfficiency=(%s)" % ",".join(V(x.get("Efficiency")) or "" for x in re_))
                ini.kv("CompressorSurgeLineFlow", V(fl.get("SurgeLineFlow")))
    return ini.text()


# ---------------------------------------------------------------------------
#  Gears.ini (+ Zeilen fuer den [DRIVELINE]-Block der HDV)
# ---------------------------------------------------------------------------
def write_gears(gears, car):
    """HDV-Zeilen im rF2-Stil (Range + Special mit Zaehnezahlen) und Gears.ini-Liste."""
    lines = []
    bev = gears.get("BevelGearRatio") or {}
    bi, bo = bev.get("NumInputCogTeeth") or 1, bev.get("NumOutputCogTeeth") or 1

    def teeth(a):
        return (a.get("NumInputCogTeeth") or 0), (a.get("NumOutputCogTeeth") or 0)

    def block(key, gr, final=False):
        avail = [teeth(a) for a in (gr or {}).get("AvailableGearRatios") or []]
        sel = (gr or {}).get("DefaultSelectedGearRatioIndex") or 0
        if not avail:
            return []
        out = ["%sRange=(0,0,%d)" % (key, len(avail)), "%sSetting=%d" % (key, sel)]
        for i, (a, b) in enumerate(avail):
            r = (b / a) if a else 0.0
            if final:
                r *= (bo / bi) if bi else 1.0
                out.append('%sSpecial=(%d,"%.3f",,"%d,%d,%d,%d")' % (key, i, r, a, b, bi, bo))
            else:
                out.append('%sSpecial=(%d,"%.3f",,"%d,%d")' % (key, i, r, a, b))
        return out

    fwd = gears.get("ForwardGearRatios") or []
    lines.append("ForwardGears=%d" % len(fwd))
    lines += block("FinalDrive", gears.get("FinalDriveGearRatios"), final=True)
    lines += block("Reverse", gears.get("ReverseGearRatios"))
    for i, g in enumerate(fwd, 1):
        lines += block("Gear%d" % i, g)

    # Gears.ini: alle verfuegbaren Uebersetzungen (fuer die Setup-Liste)
    pool = []
    for g in fwd + [gears.get("ReverseGearRatios")]:
        for a in (g or {}).get("AvailableGearRatios") or []:
            if teeth(a) not in pool:
                pool.append(teeth(a))
    out = ["// %s - Gears (konvertiert aus Rennsport)" % car, "[GEAR_RATIOS]"]
    for a, b in sorted(pool, key=lambda x: -(x[1] / x[0] if x[0] else 0)):
        out.append("ratio=(%d, %d)  // %.3f" % (a, b, (b / a) if a else 0))
    out += ["", "[FINAL_DRIVE]", "bevel=(%d, %d)" % (bi, bo)]
    for a in (gears.get("FinalDriveGearRatios") or {}).get("AvailableGearRatios") or []:
        i, o = teeth(a)
        out.append("ratio=(%d, %d)  // %.3f" % (i, o, (o / i) if i else 0))
    for name, key in (("UPSHIFT", "UpshiftConditions"), ("DOWNSHIFT", "DownshiftConditions")):
        cond = gears.get(key) or []
        if cond:
            out += ["", "// Rennsport %s-Bedingungen (nicht Teil von rF2):" % name]
            for gear, c in cond:
                out.append("// %s: RPM %s, MaxSpeed %s" % (gear, fmt_num((c or {}).get("EngineRPM") or 0.0),
                                                           fmt_num((c or {}).get("MaxCarSpeed") or 0.0)))
    return "\n".join(out) + "\n", lines


# ---------------------------------------------------------------------------
#  TBC
# ---------------------------------------------------------------------------
TBC_RENAME = {"LatCurveName": "LatCurve", "BrakingCurveName": "BrakingCurve", "TractiveCurveName": "TractiveCurve"}
TBC_SKIP = ("bUseNewTireModel", "bShowOnlyNewTireModelProperties", "Location", "TireAdvancedData",
            "bReplaceCompatiblePropertiesWithRNTMProperties", "WearGrip", "WearGripLerp", "LoadedRadius",
            "DisplayTemperatures")


def compound_name(name, strings):
    if isinstance(name, dict):
        return strings.get(name.get("key"), name.get("key"))
    return name or "Compound"


def write_tbc(tb, car, strings):
    ini = Ini()
    ini.raw("// %s - Reifen (konvertiert aus Rennsport)" % car)
    for sc in tb.get("TireSlipCurves") or []:
        ini.section("SLIPCURVE")
        ini.raw('Name="%s"' % sc.get("Name", "Default"))
        ini.kv("Step", V(sc.get("Step")))
        ini.kv("DropoffFunction", V(sc.get("DropoffFunction")) or "0.0")
        ini.raw("Data:")
        data = [V(x) or "0" for x in sc.get("Data") or []]
        for i in range(0, len(data), 10):
            ini.raw(" ".join(data[i:i + 10]))
    tgms = []
    for cp in tb.get("TireCompounds") or []:
        ini.section("COMPOUND")
        ini.raw('Name="%s"' % compound_name(cp.get("Name"), strings))
        ini.kv("WetWeather", V(cp.get("WetWeather")) or "0")
        for loc in cp.get("PerLocationData") or []:
            li = loc.get("Location", 9)
            ini.raw("%s:" % (TIRE_LOCATIONS[li] if isinstance(li, int) and li < len(TIRE_LOCATIONS) else "ALL"))
            adv = loc.get("TireAdvancedData")
            if isinstance(adv, dict):
                ini.raw('TGM="%s.tgm"' % adv["name"])
                tgms.append(adv)
            write_struct(ini, loc, TBC_RENAME, skip=TBC_SKIP)
            wg = [V(x) for x in loc.get("WearGrip") or []]
            wg = [x for x in wg if x is not None]
            for i in range(0, len(wg), 8):
                ini.raw("WearGrip%d=(%s)" % (i // 8 + 1, ",".join(wg[i:i + 8])))
    # Kurvennamen in Anfuehrungszeichen
    txt = ini.text()
    txt = re.sub(r'^(LatCurve|BrakingCurve|TractiveCurve)=(?!")(.*)$', r'\1="\2"', txt, flags=re.M)
    return txt, tgms


def read_string_table(content, path):
    """UStringTable: (leere) Properties, dann Namespace + Map<Key, SourceString>.
    Ohne Treffer wird spaeter einfach der Key benutzt (z.B. "Soft")."""
    base = game_path(content, path)
    if not base or not os.path.isfile(base + ".uasset"):
        return {}
    try:
        pkg = Package(base)
        _, data = pkg.main_export("StringTable")
    except Exception:
        return {}
    for start in (0, 4):
        try:
            r = Reader(data, start)
            v = r.u16()
            while not (v >> 8) & 1:
                v = r.u16()
            r.fstr()                     # Namespace
            n = r.i32()
            if not 0 < n < 100000:
                continue
            out = {}
            for _ in range(n):
                k = r.fstr()
                out[k] = r.fstr()
            return out
        except Exception:
            continue
    return {}


# ---------------------------------------------------------------------------
#  TGM (Reifenmodell)
# ---------------------------------------------------------------------------
#  Zwei Arten von TireAdvancedData in Rennsport:
#   a) "klassisch": QuasiStaticAnalysis + Nodes + Realtime + LookupV2 + PatchV1
#      -> 1:1 rF2-TGM (Realtime-Felder heissen nur teilweise anders)
#   b) "RNTM" (Rennsport New Tire Model): Verweise auf TireModelData,
#      TireCompoundDetailData, TireSizeDetailData, TireInternalGasData.
#      Rennsport fuellt daraus beim Laden dieselbe interne Realtime-Struktur wie
#      aus a). Die Zuordnung unten ist aus dieser Ladefunktion der Exe abgeleitet
#      (gleiche Ziel-Offsets fuer Realtime-Feld und RNTM-Feld), inkl. der dort
#      angewendeten Multiplikatoren und Kurven-Abtastung.

def _v(x):
    """ValueAsString -> str oder None"""
    if isinstance(x, dict) and "Value" in x:
        s = x.get("Value")
        return s if s not in (None, "") else None
    if isinstance(x, str):
        return x or None
    return None


def _vec(x, n):
    if not isinstance(x, dict):
        return None
    out = [_v(x.get(c)) for c in "XYZW"[:n]]
    return out if any(o is not None for o in out) else None


def _num(s, default=None):
    try:
        return float(str(s).replace("+", "")) if s not in (None, "") else default
    except ValueError:
        return default


def _fmt(x):
    if isinstance(x, str):
        return x
    if x is None:
        return "0"
    s = "%.10g" % x
    return s


def _path(d, path):
    for k in path.split("."):
        if not isinstance(d, dict):
            return None
        d = d.get(k)
    return d


def curve_eval(keys, x):
    """UE FRichCurve::Eval (konstant ausserhalb, linear/konstant/kubisch)"""
    if not keys:
        return None
    if x <= keys[0]["Time"]:
        return keys[0]["Value"]
    if x >= keys[-1]["Time"]:
        return keys[-1]["Value"]
    for a, b in zip(keys, keys[1:]):
        if a["Time"] <= x <= b["Time"]:
            dt = b["Time"] - a["Time"]
            if dt <= 0:
                return b["Value"]
            u = (x - a["Time"]) / dt
            im = a.get("Interp", 0)
            if im == 1:                          # constant
                return a["Value"]
            if im == 0 or im == 3:               # linear / none
                return a["Value"] + (b["Value"] - a["Value"]) * u
            p0, p3 = a["Value"], b["Value"]      # cubic (Bezier wie UE)
            p1 = p0 + a.get("Leave", 0.0) * dt / 3.0
            p2 = p3 - b.get("Arrive", 0.0) * dt / 3.0
            q = 1 - u
            return q * q * q * p0 + 3 * q * q * u * p1 + 3 * q * u * u * p2 + u * u * u * p3
    return keys[-1]["Value"]


def curve_keys(c):
    k = ((c or {}).get("EditorCurveData") or {}).get("Keys") or []
    return sorted((x for x in k if isinstance(x, dict)), key=lambda x: x["Time"])


# rF2-Schluessel <- Felder der Rennsport-Struktur RealtimeParametersData (klassisch)
RT_KEYS = [
    ("StaticBaseCoefficient", ["BaseStaticFrictionCoefficient"]),
    ("SlidingBaseCoefficient", ["BaseSlidingFrictionCoefficient"]),
    ("TemporaryCoefficients", ["TemporaryStaticAndSlidingFrictionCoefficients"]),
    ("StaticDiffusiveAdhesion", ["StaticDiffusiveAdhesion"]),
    ("SlidingDiffusiveAdhesion", ["SlidingDiffusiveAdhesion"]),
    ("AbrasionCurveWLFStartStep", ["AbrasionCurveWLFStartStep"]),
    ("AbrasionVolumePerUnitEnergy", ["AbrasionCurveVolumePerUnitEnergy"]),
    ("TemporaryAbrasion", ["TemporaryAbrasion"]),
    ("DegradationPerWearFraction", ["DegradationCurvePerWearFraction"]),
    ("DegradationCurveParameters", ["DegradationCurveParameters"]),
    ("DegradationPerUnitHistory", ["DegradationCurvePerUnitHistory"]),
    ("MassInertiaMultiplier", ["MassInertiaMultiplier"]),
    ("SizeMultiplier", ["SizeMultiplier"]),
    ("LoadVsDeflectionMultiplier", ["LoadVsDeflectionMultiplier"]),
    ("InclinationExtrapolation", ["InclinationExtrapolation"]),
    ("LateralDistributionMultiplier", ["LateralDistributionMultiplier"]),
    ("LongitudinalDistributionMultiplier", ["LongitudinalDistributionMultiplier"]),
    ("RingStiffnessMultiplier", ["RingLinearStiffnessMultiplier", "RingAngularStiffnessMultiplier"]),
    ("TemporaryRingMassInertia", ["TemporaryRingMassInertia"]),
    ("TemporaryRingDamper", ["TemporaryRingLinearDamper", "TemporaryRingAngularDamper"]),
    ("SpringConditions", ["SpringConditions"]),
    ("TemporaryBeltSpring", ["TemporaryBeltSpring"]),
    ("BeltSpringX", ["BeltSpringX"]),
    ("BeltSpringZ", ["BeltSpringZ"]),
    ("TemporaryBeltDamper", ["TemporaryBeltDamper"]),
    ("TemporaryBristleSpring", ["TemporaryBristleSpring"]),
    ("BaseSpringPerUnitArea", ["BaseSpringPerUnitArea"]),
    ("TreadSpringXPerUnitArea", ["TreadSpringXPerUnitArea"]),
    ("TreadSpringZPerUnitArea", ["TreadSpringZPerUnitArea"]),
    ("TemporaryBristleDamper", ["TemporaryBristleDamper"]),
    ("BaseDamperPerUnitArea", ["BaseDamperPerUnitArea"]),
    ("HystereticVerticalDamperPerUnitArea", ["HystereticVerticalDamperPerUnitArea"]),
    ("VerticalDampingMultiplier", ["BristleVerticalDampingMultiplier"]),
    ("MarbleEffectOnEffectiveLoad", ["MarbleEffectOnEffectiveLoad"]),
    ("TerrainWeightOnContactTemperature", ["TerrainWeightOnContactTemperature"]),
    ("StaticRoughnessEffect", ["StaticRoughnessEffect"]),
    ("WLFParameters", ["WLFParameters"]),
    ("StaticCurve", ["StaticCurve"]),
    ("SlidingAdhesionCurve", ["SlidingAdhesionCurve"]),
    ("SlidingMicroDeformationCurve", ["SlidingMicroDeformationCurve"]),
    ("SlidingMacroDeformationCurve", ["SlidingMacroDeformationCurve"]),
    ("RubberPressureSensitivityPower", ["RubberPressureSensitivityPower"]),
    ("RubberPressureSensitivityTableParams", ["RubberPressureSensitivityTableParams"]),
    ("RubberPressureSensitivityTableEntries", ["RubberPressureSensitivityTableEntries"]),
    ("IgnitionParameters", ["IgnitionParameters"]),
    ("GrooveEffects", ["GrooveEffects"]),
    ("GrooveSqrdEffects", ["GrooveSqrdEffects"]),
    ("DampnessEffects", ["DampnessEffects"]),
    ("TemporaryGripLossForWetness", ["TemporaryGripLossForWetness"]),
    ("ThermalDepthAtSurface", ["ThermalDepthAtSurface"]),
    ("ThermalDepthBelowSurface", ["ThermalDepthBelowSurface"]),
    ("BristleLength", ["BristleLength"]),
    ("MaxRadiusWithExtension", ["MaxRadiusWithExtension"]),
    ("TemporaryIncludeDampingHeat", ["TemporaryIncludeDampingHeat"]),
    ("DampingHeatEnergy", ["DampingHeatEnergy"]),
    ("InternalGasHeatTransfer", ["InternalGasHeatTransfer"]),
    ("ExternalGasHeatTransfer", ["ExternalGasHeatTransfer"]),
    ("GroundContactConductance", ["GroundContactConductance"]),
    ("GroundConductance", ["GroundConductance"]),
    ("WetConductance", ["WetConductance"]),
    ("TireRadiationEmissivity", ["TireRadiationEmissivity"]),
    ("DryTerrainEffect", ["DryTerrainEffect"]),
    ("WetTerrainEffect", ["WetTerrainEffect"]),
    ("GrassTerrainEffect", ["GrassTerrainEffect"]),
    ("DirtTerrainEffect", ["DirtTerrainEffect"]),
    ("GravelTerrainEffect", ["GravelTerrainEffect"]),
    ("RumbleTerrainEffect", ["RumbleTerrainEffect"]),
    ("SpecialTerrainEffect", ["SpecialTerrainEffect"]),
    ("GaugePressureExtrapolationRange", ["GaugePressureExtrapolationRange"]),
    ("CarcassTemperatureExtrapolationRange", ["CarcassTemperatureExtrapolationRange"]),
    ("RotationSquaredExtrapolationRange", ["RotationSquaredExtrapolationRange"]),
    ("InternalGasMolarMass", ["InternalGasMolarMass"]),
    ("InternalGasSpecificHeatAtConstantVolume", ["InternalGasSpecificHeatAtConstantVolume"]),
]
RT_ORDER = [k for k, _ in RT_KEYS]
RT_REPEAT = ("InternalGasSpecificHeatAtConstantVolume",)


def _components(x):
    """beliebiger Realtime-Wert -> Liste von Strings (oder Liste von Listen bei Wiederholung)"""
    if x is None:
        return None
    if isinstance(x, list):
        if x and isinstance(x[0], dict) and set(x[0]) <= {"X", "Y", "Z", "W"}:
            return [[_v(e.get(c)) or "0" for c in "XYZW" if c in e] for e in x]
        vals = [_v(e) for e in x]
        vals = [v for v in vals if v is not None]
        return vals or None
    if isinstance(x, dict) and "Value" in x:
        v = _v(x)
        return [v] if v is not None else None
    if isinstance(x, dict) and set(x) <= {"X", "Y", "Z", "W"}:
        n = max("XYZW".index(c) for c in x) + 1
        vals = [_v(x.get(c)) for c in "XYZW"[:n]]
        if all(v is None for v in vals):
            return None
        return [v if v is not None else "0" for v in vals]
    return None


def realtime_from_classic(rt):
    out = {}
    for key, fields in RT_KEYS:
        if key in RT_REPEAT:
            c = _components(rt.get(fields[0]))
            if c:
                out[key] = c
            continue
        vals = []
        ok = False
        for f in fields:
            c = _components(rt.get(f))
            if c:
                ok = True
                vals += c
        if ok:
            out[key] = vals
    return out


def realtime_from_rntm(base, comp, size, gas, qsa):
    """RNTM-Daten -> rF2-Realtime (Reihenfolge/Formeln wie in Rennsport)"""
    rt = dict(base or {})
    S = lambda p: _v(_path(size, p))           # noqa: E731
    C = lambda p: _v(_path(comp, p))           # noqa: E731

    def put(key, vals, n=None):
        if vals is None or all(v is None for v in vals):
            return
        old = list(rt.get(key) or [])
        n = n or len(vals)
        old += ["0"] * (n - len(old))
        for i, v in enumerate(vals):
            if v is not None:
                old[i] = v if isinstance(v, str) else _fmt(v)
        rt[key] = old[:n]

    def mul(key, idxs, m):
        if m is None or key not in rt:
            return
        for i in idxs:
            if i < len(rt[key]):
                x = _num(rt[key][i])
                if x is not None:
                    rt[key][i] = _fmt(x * m)

    if size:
        put("TemporaryRingMassInertia", [S("RingOverrides.TemporaryRingMassOverride"),
                                         S("RingOverrides.TemporaryLateralRingInertiaOverride"),
                                         S("RingOverrides.TemporaryLongitudinalRingInertiaOverride"),
                                         S("RingOverrides.TemporaryVerticalRingInertiaOverride")])
        put("TemporaryRingDamper", [S("RingOverrides.TemporaryLateralRingLinearDamper"),
                                    S("RingOverrides.TemporaryLongitudinalRingLinearDamper"),
                                    S("RingOverrides.TemporaryVerticalRingLinearDamper"),
                                    S("RingOverrides.TemporaryRollRingAngularDamper"),
                                    S("RingOverrides.TemporaryPitchRingAngularDamper"),
                                    S("RingOverrides.TemporaryYawRingAngularDamper")], 6)
        put("MassInertiaMultiplier", [S("MassMultiplier"), S("LateralInertiaMultiplier"),
                                      S("LongitudinalInertiaMultiplier"), S("VerticalInertiaMultiplier")], 4)
        put("LateralDistributionMultiplier", [S("LateralDistributionMultiplier")])
        put("LongitudinalDistributionMultiplier", [S("LongitudinalDistributionMultiplier")])
        rs = _path(size, "RingStiffness") and size["RingStiffness"]
        if rs:
            b, lv, p_, yr = (S("RingStiffness.StiffnessBase"), S("RingStiffness.StiffnessLongitudinalVertical"),
                             S("RingStiffness.StiffnessPitch"), S("RingStiffness.StiffnessYawRoll"))
            put("RingStiffnessMultiplier", [b, lv, lv, p_, yr, yr], 6)
        put("TemporaryBeltDamper", [S("BeltOverrides.TemporaryLateralBeltDamper"),
                                    S("BeltOverrides.TemporaryLongitudinalBeltDamper")], 2)
        put("TemporaryBeltSpring", [S("BeltOverrides.TemporaryLateralBeltSpringBase"),
                                    S("BeltOverrides.TemporaryLongitudinalBeltSpringBase")], 2)
        put("TemporaryBristleSpring", [S("TreadBristleOverrides.TemporaryLateralBristleSpringPerUnitArea"),
                                       S("TreadBristleOverrides.TemporaryTreadBristleSpringYComponent"),
                                       S("TreadBristleOverrides.TemporaryLongitudinalBristleSpringPerUnitArea")], 3)
        put("TemporaryBristleDamper", [S("TreadBristleOverrides.TemporaryLateralBristleDamper"),
                                       S("TreadBristleOverrides.TemporaryLongitudinalBristleDamper"),
                                       S("TreadBristleOverrides.TemporaryVerticalBristleDamper")], 3)
        put("GaugePressureExtrapolationRange", [S("QsaExtrapolation.GaugePressureExtrapolationRangeMin"),
                                                S("QsaExtrapolation.GaugePressureExtrapolationRangeMax")], 2)
        put("CarcassTemperatureExtrapolationRange", [S("QsaExtrapolation.CarcassTemperatureExtrapolationRangeMin"),
                                                     S("QsaExtrapolation.CarcassTemperatureExtrapolationRangeMax")], 2)
        put("RotationSquaredExtrapolationRange", [S("QsaExtrapolation.RotationSquaredExtrapolationRangeMin"),
                                                  S("QsaExtrapolation.RotationSquaredExtrapolationRangeMax")], 2)
        put("SpringConditions", [S("BeltTreadSpring.SpringConditionBaseGaugePressure"),
                                 S("BeltTreadSpring.SpringConditionBaseTemp"),
                                 S("BeltTreadSpring.SpringBaseConditionRotationSquared")], 3)
        for key, p in (("BeltSpringX", "LateralBeltSpring"), ("BeltSpringZ", "LongitudinalBeltSpring")):
            put(key, [S(p + ".BeltSpringBase"), S(p + ".BeltSpringUnitPerPressure"),
                      S(p + ".BeltSpringUnitPerTemp"), S(p + ".BeltSpringUnitPerRotationSquared")], 4)
        put("BaseSpringPerUnitArea", [S("BaseTreadBristleSpring.LateralBaserBristleSpringPerUnitArea"),
                                      S("BaseTreadBristleSpring.BaseTreadBristleSpringYComponent"),
                                      S("BaseTreadBristleSpring.LongitudinalBaseBristleSpringPerUnitArea")], 3)
        for key, p in (("TreadSpringXPerUnitArea", "LateralTreadBristleSpring"),
                       ("TreadSpringZPerUnitArea", "LongitudinalTreadBristleSpring")):
            put(key, [S(p + ".TreadSpringBase"), S(p + ".TreadSpringPressure"),
                      S(p + ".TreadSpringTemp"), S(p + ".TreadSpringRotationSquared")], 4)
        put("BaseDamperPerUnitArea", [S("TreadBristleDamper.LateralTreadBaseDamperPerUnitArea"),
                                      S("TreadBristleDamper.LongitudinalTreadBaseDamperPerUnitArea"),
                                      S("TreadBristleDamper.VerticalTreadBaseDamperPerUnitArea")], 3)
        put("HystereticVerticalDamperPerUnitArea", [S("HystereticVerticalDamperPerUnitArea")])
        bv = [_v(x) for x in size.get("BristleVerticalDampingMultiplier") or []]
        if any(bv):
            rt["VerticalDampingMultiplier"] = [x or "1" for x in bv]
        put("ThermalDepthAtSurface", [S("TreadBristleThermal.ThermalDepthAtSurface")])
        put("ThermalDepthBelowSurface", [S("TreadBristleThermal.ThermalDepthBelowSurface")])
        put("BristleLength", [S("BristleLength")])
        put("MaxRadiusWithExtension", [S("MaxRadiusWithExtension")])
        put("InclinationExtrapolation", [S("InclinationExtrapolation")])
        norm = S("RubberPressure.SensitivityPowerNormalize")
        put("RubberPressureSensitivityPower", [S("RubberPressure.SensitivityPower"),
                                               S("RubberPressure.SensitivityPowerZeroPressureOffset"),
                                               S("RubberPressure.SensitivityPowerNominalMax"),
                                               None if norm is None else ("1" if _num(norm, 0) else "0")], 4)
        put("RubberPressureSensitivityTableParams", [S("RubberPressure.SensitivityTableStepSize"),
                                                     S("RubberPressure.SensitivityTableInitialSlope"),
                                                     S("RubberPressure.SensitivityTableFinalSlope")], 3)
        te = [_v(x) for x in _path(size, "RubberPressure.SensitivityTableEntries") or []]
        if any(te):
            rt["RubberPressureSensitivityTableEntries"] = [x or "1" for x in te]
        put("TerrainWeightOnContactTemperature", [S("TerrainWeightOnContactTemperature")])
        put("TemporaryIncludeDampingHeat", [S("TemporaryIncludeDampingHeat")])
        put("DampingHeatEnergy", [S("TreadBristleThermal.DampingHeatEnergySidewallFraction"),
                                  S("TreadBristleThermal.DampingHeatEnergyCarcassFraction"),
                                  S("TreadBristleThermal.DampingHeatEnergyTreadFraction")], 3)
        for k in ("Dry", "Wet", "Grass", "Dirt", "Gravel", "Rumble", "Special"):
            p = k + "TerrainEffect"
            put(p, [S(p + ".StaticFriction"), S(p + ".SlidingFriction"), S(p + ".Heating")], 3)

    if comp:
        put("TemporaryGripLossForWetness", [C("TemporaryGripLossForWetness")])
        put("SizeMultiplier", [C("SizeMultipliers.TireSizeMultiplier"), C("SizeMultipliers.TireRadiusMultiplier")], 2)
        put("LoadVsDeflectionMultiplier", [C("LoadDeflectionMultipliers.LoadVsDeflectionMultiplier")])
        put("MarbleEffectOnEffectiveLoad", [C("MarbleEffectOnEffectiveLoad")])
        ts, tl = C("TemporaryStaticFrictionBaseCoefficient"), C("TemporarySlidingFrictionBaseCoefficient")
        if ts and tl:
            put("TemporaryCoefficients", [ts, tl], 2)
        put("StaticBaseCoefficient", [C("StaticFrictionBaseCoefficient")])
        put("SlidingBaseCoefficient", [C("SlidingFrictionBaseCoefficient")])
        put("StaticDiffusiveAdhesion", [C("StaticAdhesion.StaticDiffuseAdhesionHalfTime"),
                                        C("StaticAdhesion.StaticDiffuseAdhesionBasePressure"),
                                        C("StaticAdhesion.StaticDiffuseAdhesionCurveInfluenceFraction")], 3)
        put("SlidingDiffusiveAdhesion", [C("SlidingAdhesion.SlidingDiffuseAdhesionHalfTime"),
                                         C("SlidingAdhesion.SlidingDiffuseAdhesionBasePressure"),
                                         C("SlidingAdhesion.SlidingDiffuseAdhesionCurveInfluenceFraction")], 3)
        put("StaticRoughnessEffect", [C("StaticRoughnessEffect")])
        put("WLFParameters", [C("WlfGlassTemp"), C("WlfGlassTempOffsetToReference"),
                              C("WlfGlassTempDividendMultiplier"), C("WlfGlassTempDivisorAddition")], 4)
        put("GrooveEffects", [C("GrooveOnStaticGrip"), C("GrooveOnSlidingAdhesion"),
                              C("GrooveOnSlidingMicroDeformation"), C("GrooveOnSlidingMacroDeformation")], 4)
        put("GrooveSqrdEffects", [C("GrooveSquaredOnStaticGrip"), C("GrooveSquaredOnSlidingAdhesion"),
                                  C("GrooveSquaredOnSlidingMicroDeformation"),
                                  C("GrooveSquaredOnSlidingMacroDeformation")], 4)
        put("DampnessEffects", [C("GripDampness.DampnessEffectOnStaticGrip"),
                                C("GripDampness.DampnessEffectOnSlidingAdhesion"),
                                C("GripDampness.DampnessEffectOnSlidingMicroDeformation"),
                                C("GripDampness.DampnessEffectOnSlidingMacroDeformation")], 4)
        # Kurven: (X1,Y1,X2,Y2,X3,Y3); Gleitkurven liegen in log10 vor -> * ln(10)
        sg = "StaticGripCurve."
        vals = [C(sg + k) for k in ("ColdTemp", "ColdMultiplier", "OptimumTemp", "OptimumMultiplier",
                                    "OverheatTemp", "OverheatMultiplier")]
        if all(v is not None for v in vals):
            rt["StaticCurve"] = vals
        for key, p in (("SlidingAdhesionCurve", "SlidingAdhesionCurve"),
                       ("SlidingMicroDeformationCurve", "MicroDeformationCurve"),
                       ("SlidingMacroDeformationCurve", "MacroDeformationCurve")):
            vals = [_num(C(p + "." + k)) for k in ("XLow", "YLow", "XMid", "YMid", "XHi", "YHi")]
            if all(v is not None for v in vals):
                for i in (0, 2, 4):
                    vals[i] *= 2.302585092994046
                rt[key] = [_fmt(v) for v in vals]
        # Abrieb: 32 Stuetzstellen der Kurve * MinAbrasionVolumePerUnitEnergy
        mn = _num(C("MinAbrasionVolumePerUnitEnergyValue"))
        keys = curve_keys(comp.get("AbrasionMultipliers"))
        if mn is not None and keys and keys[0]["Time"] != keys[-1]["Time"]:
            t0, t1 = keys[0]["Time"], keys[-1]["Time"]
            step = (t1 - t0) / 31.0
            rt["AbrasionCurveWLFStartStep"] = [_fmt(t0), _fmt(step)]
            rt["AbrasionVolumePerUnitEnergy"] = [_fmt(curve_eval(keys, t0 + i * step) * mn) for i in range(32)]
        put("TemporaryAbrasion", [C("TemporaryAbrasion")])
        put("DegradationCurveParameters", [C("WearingHeatHistoryTempKelvin"), C("WearingHeatHistoryStep")], 2)
        for key, p in (("DegradationPerWearFraction", "DegradationPerWearFraction"),
                       ("DegradationPerUnitHistory", "DegradationPerUnitHistory")):
            keys = curve_keys(comp.get(p))
            rt[key] = [_fmt(curve_eval(keys, i / 31.0) if keys else 1.0) for i in range(32)]
        put("IgnitionParameters", [C("RubberIgnitionTemp"), C("RubberIgnitionSurfaceHeatMultiplier"),
                                   C("RubberIgnitionNominalMaxTemp")], 3)
        put("TireRadiationEmissivity", [C("TireRadiationEmissivity")])
        put("GroundContactConductance", [C("GroundContactConductance")])
        put("GroundConductance", [C("Conductance.GroundConductanceBase"),
                                  C("Conductance.GroundConductanceIncreasePerUnitPressure")], 3)
        put("WetConductance", [C("Conductance.WetConductanceSurfaceDampness"),
                               C("Conductance.WetConductanceStandingWater")], 4)
        put("InternalGasHeatTransfer", [C("InternalHeatTransfer.InternalGasHeatTransferBase"),
                                        C("InternalHeatTransfer.InternalGasHeatTransferSpeed"),
                                        C("InternalHeatTransfer.InternalGasHeatTransferExponent")], 3)
        put("ExternalGasHeatTransfer", [C("ExternalHeatTransfer.ExternalGasHeatTransferBase"),
                                        C("ExternalHeatTransfer.ExternalGasHeatTransferSpeed"),
                                        C("ExternalHeatTransfer.ExternalGasHeatTransferExponent")], 3)
        # Multiplikatoren aus dem Compound (wie Rennsport nach dem Laden)
        m = _num(C("DampingMultipliers.RingDamperMultiplier"))
        mul("TemporaryRingDamper", range(6), m)
        m = _num(C("DampingMultipliers.BristleDamperMultiplier"))
        mul("TemporaryBristleDamper", range(3), m)
        mul("BaseDamperPerUnitArea", range(3), m)
        mul("HystereticVerticalDamperPerUnitArea", [0], _num(C("DampingMultipliers.HystereticDamperMultiplier")))
        m = _num(C("SpringStiffnessMultipliers.LateralBaseSpringStiffnessMultiplier"))
        mul("TreadSpringXPerUnitArea", range(4), m)
        m = _num(C("SpringStiffnessMultipliers.LongitudinalBaseSpringStiffnessMultiplier"))
        mul("TreadSpringZPerUnitArea", range(4), m)
        mul("BeltSpringX", range(4), _num(C("BeltStiffnessMultipliers.LateralBeltStiffnessMultiplier")))
        mul("BeltSpringZ", range(4), _num(C("BeltStiffnessMultipliers.LongitudinalBeltStiffnessMultiplier")))
        mul("LateralDistributionMultiplier", [0],
            _num(C("ForceDistributionMultipliers.LateralDistributionMultiplier")))
        mul("LongitudinalDistributionMultiplier", [0],
            _num(C("ForceDistributionMultipliers.LongitudinalDistributionMultiplier")))

    if size:
        # Groessen-Anpassung relativ zum Grundmodell
        tw, tr = _num(_v((qsa or {}).get("TotalWidth"))), _num(_v((qsa or {}).get("TotalRadius")))
        rw, rr = _num(S("RequestedTireWidth")), _num(S("RequestedTireRadius"))
        if "SizeMultiplier" not in rt:
            rt["SizeMultiplier"] = ["1", "1"]
        if rw and tw:
            mul("SizeMultiplier", [0], rw / tw)
        mul("SizeMultiplier", [0], _num(S("TireWidthMultiplier")))
        if rr and tr:
            mul("SizeMultiplier", [1], rr / tr)
        mul("SizeMultiplier", [1], _num(S("TireRadiusMultiplier")))
        m = _num(S("GroundConductanceMultiplier"))
        mul("GroundConductance", [0], m)
        mul("WetConductance", [0, 1], m)
        mul("TireRadiationEmissivity", [0], _num(S("AirDissipationMultiplier")))
        mul("LoadVsDeflectionMultiplier", [0], _num(S("VerticalDeflectionMultiplier")))

    if gas:
        g = gas.get("InternalGasData") or gas
        put("InternalGasMolarMass", [_v(g.get("InternalGasMolarMass"))])
        sh = [[_v(e.get("TemperatureKelvin")) or "0", _v(e.get("SpecificHeatAtConstVolume")) or "0"]
              for e in g.get("GasTemperatureLookupData") or [] if isinstance(e, dict)]
        if sh:
            rt["InternalGasSpecificHeatAtConstantVolume"] = sh
    return rt


QSA_KEYS = [("NumLayers", "NumLayers"), ("NumSections", "NumSections"), ("RimVolume", "RimVolume"),
            ("DisplaceBulkMassWithPly", "DisplaceBulkMassWithPly"),
            ("PlyCompressionTensionTransition", "PlyCompressionTensionTransition"),
            ("UserDTMultiplier", "UserDTMultiplier"), ("RealtimeCamberLimit", "RealtimeCamberLimit"),
            ("CalcPointAccel", "CalculatePointAcceleration"), ("LateralTestForce", "LateralTestForce"),
            ("LongitudinalTestForce", "LongitudinalTestForce"), ("GaugePressure", "GaugePressure"),
            ("CarcassTemperature", "CarcassTemperature"), ("RotationSquared", "RotationSquared"),
            ("NumNodes", "NumNodes"), ("TotalMass", "TotalMass"),
            ("TotalInertiaStandard", "TotalInertiaStandard"), ("RingMass", "RingMass"),
            ("RingInertiaStandard", "RingInertiaStandard")]
MAT_KEYS = ("Temperature", "Density", "YoungsModulus", "PoissonsRatio", "CompressToTensRatio",
            "SpecificHeat", "ThermalConductivity")
PATCH_TAGS = ("MID", "LGP", "HGP", "LCT", "HCT", "LRS", "HRS", "NFX", "PFX", "NFZ", "PFZ")


def _tuple(vals):
    return "(" + ",".join(vals) + ")"


def tgm_text(name, qsa, nodes, mirror, rt, lookup, patch, note=""):
    L = ["//[[gMa1.002f (c)2016    ]] [[            ]]"]
    L.append("// %s - konvertiert aus Rennsport (rennsport_rf2.py)%s" % (name, note))
    L.append("[QuasiStaticAnalysis]")
    for key, f in QSA_KEYS:
        x = (qsa or {}).get(f)
        if isinstance(x, list):
            for e in x:
                v = _v(e)
                if v is not None:
                    L.append("%s=%s" % (key, v))
            continue
        c = _components(x)
        if c:
            L.append("%s=%s" % (key, c[0] if len(c) == 1 else _tuple(c)))
    L.append("")
    for i, nd in enumerate(nodes or []):
        L.append("[Node] // %d" % i)
        for key, f, n in (("Geometry", "Geometry", 3), ("InnerGeometryOverride", "InnerGeometryOverride", 2)):
            c = _vec(nd.get(f), n)
            if c:
                L.append("%s=%s" % (key, _tuple([x or "0" for x in c])))
        for m in nd.get("BulkMaterials") or []:
            L.append("BulkMaterial=%s" % _tuple([_v(m.get(k)) or "0" for k in MAT_KEYS]))
        c = _vec(nd.get("AnisoCarcassConductivityMultipliers"), 3)
        if c:
            L.append("AnisoCarcassConductivityMult=%s" % _tuple([x or "0" for x in c]))
        if _v(nd.get("TreadDepth")) is not None:
            L.append("TreadDepth=%s" % _v(nd.get("TreadDepth")))
        for m in nd.get("TreadMaterials") or []:
            L.append("TreadMaterial=%s" % _tuple([_v(m.get(k)) or "0" for k in MAT_KEYS]))
        c = _vec(nd.get("RingAndRim"), 2)
        if c:
            L.append("RingAndRim=%s" % _tuple([x or "0" for x in c]))
        for ply in nd.get("PlyData") or []:
            c = _vec(ply.get("PlyParams"), 3)
            if c:
                L.append("PlyParams=%s" % _tuple([x or "0" for x in c]))
            for m in ply.get("PlyMaterials") or []:
                L.append("PlyMaterial=%s" % _tuple([_v(m.get(k)) or "0" for k in MAT_KEYS]))
        L.append("")
    cpa = _v((mirror or {}).get("bComplementPlyAngles"))
    if cpa is not None:
        L += ["[MirrorNodesAbove]", "ComplementPlyAngles=%s" % cpa, ""]
    L.append("[Realtime]")
    for key in RT_ORDER:
        v = rt.get(key)
        if not v:
            continue
        if key in RT_REPEAT:
            for e in v:
                L.append("%s=%s" % (key, _tuple(e)))
        elif len(v) == 1 and key not in ("AbrasionVolumePerUnitEnergy", "DegradationPerWearFraction",
                                         "DegradationPerUnitHistory", "VerticalDampingMultiplier",
                                         "RubberPressureSensitivityTableEntries"):
            L.append("%s=%s" % (key, v[0]))
        else:
            L.append("%s=%s" % (key, _tuple(v)))
    L.append("")
    if lookup:
        ver, data, chk = lookup
        L += ["[LookupV2]", "Version=%s" % ver]
        L += ["P=" + x for x in data]
        if chk is not None:
            L.append("Checksum=%s" % chk)
        L.append("")
    if patch:
        L += patch + [""]
    return "\n".join(L) + "\n"


def _patch_lines(pv, version):
    if not pv:
        return None
    out = ["[PatchV1]", "Version=%s" % version]
    st = _v(pv.get("DeflectionStepSize"))
    if st:
        out.append("DeflectionStepSize=%s" % st)
    raw = [x for x in pv.get("RawData") or [] if isinstance(x, str)]
    dd, dr, ck = pv.get("DeflectionData") or [], pv.get("DeflectionRun") or [], pv.get("Checksum") or []
    if dd:
        for i, blk in enumerate(dd):
            out.append("%s:" % (PATCH_TAGS[i] if i < len(PATCH_TAGS) else "UNK"))
            for r in (dr[i] if i < len(dr) else {}).get("Data") or []:
                out.append("R=" + r)
            for d_ in (blk or {}).get("Data") or []:
                out.append("D=" + d_)
            c = _vec(ck[i], 2) if i < len(ck) else None
            if c:
                out.append("C=(%s,%s)" % (c[0] or "0", c[1] or "0"))
        return out
    if raw:
        # Rohzeilen: je Block Tag, 2x R, n x D, C
        blk = []
        for line in raw:
            if re.match(r"^[A-Z]{3}:$", line):
                blk = [line]
                out.append(line)
                continue
            if line.startswith(("R=", "D=", "C=")):
                out.append(line)
            elif line.startswith("("):
                out.append("C=" + line)
            else:
                blk.append(line)
                out.append(("R=" if len(blk) <= 3 else "D=") + line)
        return out
    return None


def build_tgm(content, adv_ref, name):
    """TireAdvancedData (+ verknuepfte RNTM-Assets) -> TGM-Text"""
    b = game_path(content, adv_ref.get("path"))
    if not b or not os.path.isfile(b + ".uasset"):
        return None, "nicht gefunden: %s" % adv_ref.get("path")
    adv, _ = decode(b, "TireAdvancedData")

    def load(ref, cls):
        if not isinstance(ref, dict) or not ref.get("path"):
            return None
        bb = game_path(content, ref["path"])
        if not bb or not os.path.isfile(bb + ".uasset"):
            log("  [!] nicht gefunden: %s" % ref["path"])
            return None
        return decode(bb, cls)[0]

    model = load(adv.get("TireModelData"), "TireModelData") or adv
    comp = (load(adv.get("CompoundDetailData"), "TireCompoundDetailData") or {}).get("CompoundData")
    size = (load(adv.get("TireSizeDetailData"), "TireSizeDetailData") or {}).get("TireSizeData")
    gas = load(adv.get("InternalGasData"), "TireInternalGasData")
    qsa = model.get("QuasiStaticAnalysis") or adv.get("QuasiStaticAnalysis")
    nodes = model.get("Nodes") or adv.get("Nodes")
    if not qsa or not nodes:
        return None, "kein QuasiStaticAnalysis/Nodes"
    rt = realtime_from_classic(adv.get("Realtime") or {})
    rntm = bool(comp or size or gas)
    if rntm:
        rt = realtime_from_rntm(rt, comp, size, gas, qsa)
    lv = model.get("LookupV2") or adv.get("LookupV2") or {}
    pv = model.get("PatchV1") or adv.get("PatchV1") or {}
    ver = _v(lv.get("Version"))
    lookup = patch = None
    note = ""
    if ver and _num(ver, 0) < 2 and lv.get("Data"):
        lookup = (ver, [x for x in lv["Data"] if isinstance(x, str)], _v(lv.get("Checksum")))
        patch = _patch_lines(pv, ver)
    elif ver:
        note = " - LookupV2 Version %s (Rennsport-eigen) weggelassen, rF2 berechnet die Tabellen selbst" % ver
    if rntm:
        note += " - Realtime aus Rennsport-RNTM-Daten berechnet"
    return tgm_text(name, qsa, nodes, adv.get("MirrorNodesAbove") or model.get("MirrorNodesAbove"),
                    rt, lookup, patch, note), None


# ===========================================================================
#  Fahrzeug finden & konvertieren
# ===========================================================================
def game_path(content, gp):
    if not gp or not gp.startswith("/Game/"):
        return None
    return os.path.join(content, *gp[6:].split("/"))


def find_car_dirs(content):
    base = os.path.join(content, "Blueprints", "Configs", "Cars")
    out = {}
    for f in glob.glob(os.path.join(base, "**", "*_PhysicsData.uasset"), recursive=True):
        d = os.path.dirname(f)
        out[os.path.basename(d)] = d
    return out


def resolve_car(content, arg):
    a = arg.strip().strip('"').rstrip("\\/")
    if os.path.isdir(a) and glob.glob(os.path.join(a, "*_PhysicsData.uasset")):
        return os.path.abspath(a)
    cars = find_car_dirs(content)
    for k, v in cars.items():
        if k.lower() == a.lower():
            return v
    cand = [v for k, v in cars.items() if a.lower() in k.lower()]
    return cand[0] if len(cand) == 1 else None


def content_from_car_dir(d):
    p = os.path.abspath(d)
    while p and os.path.basename(p).lower() != "content":
        np_ = os.path.dirname(p)
        if np_ == p:
            return None
        p = np_
    return p


def convert(content, car_dir, out_dir, dump_json=False):
    car = os.path.basename(car_dir)
    phys_file = glob.glob(os.path.join(car_dir, "*_PhysicsData.uasset"))[0][:-7]
    log("\n=== %s ===" % car)
    phys, ppkg = decode(phys_file, "VehiclePhysicsData")
    log("  PhysicsData gelesen")
    dump = {"PhysicsData": phys}
    files = {}
    os.makedirs(out_dir, exist_ok=True)

    def load_ref(ref, cls):
        if not isinstance(ref, dict) or not ref.get("path"):
            return None
        b = game_path(content, ref["path"])
        if not b or not os.path.isfile(b + ".uasset"):
            log("  [!] nicht gefunden: %s" % ref["path"])
            return None
        data, _ = decode(b, cls)
        log("  %s gelesen: %s" % (cls, ref["name"]))
        return data

    # Chassis
    ch = load_ref(phys.get("Suspension", {}).get("Chassis"), "VehicleChassisData")
    if ch:
        dump["ChassisData"] = ch
        files["chassis"] = "%s_Chassis.ini" % car
        with open(os.path.join(out_dir, files["chassis"]), "w", encoding="utf-8") as fh:
            fh.write(write_chassis(ch, car))
    # Engine
    eng = load_ref(phys.get("Engine"), "EngineData")
    if eng:
        dump["EngineData"] = eng
        files["engine"] = "%s_Engine.ini" % car
        g = eng.get("GlobalData", {})
        files["engine_mults"] = {"GeneralTorqueMult": V(g.get("GeneralTorqueMultiplier")),
                                 "GeneralPowerMult": V(g.get("GeneralPowerMultiplier"))}
        with open(os.path.join(out_dir, files["engine"]), "w", encoding="utf-8") as fh:
            fh.write(write_engine(eng, car))
    # Elektromotor
    mot = load_ref(phys.get("ElectricMotor"), "ElectricMotorData")
    if mot:
        dump["ElectricMotorData"] = mot
        files["motor"] = "%s_Motor.ini" % car
        files["motor_linked"] = phys.get("General", {}).get("VehicleType") != 1
        etxt = None
        if not files["motor_linked"] and eng:
            etxt = write_engine(eng, car)
            # reine Elektroautos: Engine.ini wird nicht gebraucht
            ep = os.path.join(out_dir, files.get("engine") or "")
            if files.get("engine") and os.path.isfile(ep):
                os.remove(ep)
            files["engine"] = None
        mstr = {}
        for x in (phys.get("Driveline") or {}).get("MotorGeneratorUnitKineticDeliveryModeTexts") or []:
            if isinstance(x, dict) and x.get("table"):
                mstr = read_string_table(content, x["table"].split(".")[0])
                break
        with open(os.path.join(out_dir, files["motor"]), "w", encoding="utf-8") as fh:
            fh.write(write_motor(content, mot, car, phys, etxt, mstr))
    files["curves"] = {}
    for k in ("BatteryChargeWithSOCCurve", "BatteryDischargeWithSOCCurve",
              "BatteryChargeWithRPMCurve", "BatteryDischargeWithRPMCurve"):
        try:
            c = load_curve(content, phys.get("General", {}).get(k))
        except Exception:
            c = None
        if c:
            files["curves"][k] = curve_text(c)
    ct = phys.get("Driveline", {}).get("MaximumCombinedTorqueCurve")
    if isinstance(ct, dict) and ct.get("path"):
        try:
            c = load_curve(content, ct)
            if c:
                files["combined_torque"] = curve_text(c)
        except Exception:
            pass
    # Gears
    gears = load_ref(phys.get("Driveline", {}).get("Gears"), "GearsData")
    if gears:
        dump["GearsData"] = gears
        txt, lines = write_gears(gears, car)
        files["gear_lines"] = lines
        with open(os.path.join(out_dir, "%s_Gears.ini" % car), "w", encoding="utf-8") as fh:
            fh.write(txt)
    # Reifen
    written_tgm = set()
    tbs = phys.get("General", {}).get("TireBrandData") or []
    for i, ref in enumerate(tbs):
        tb = load_ref(ref, "TireBrandData")
        if not tb:
            continue
        dump.setdefault("TireBrandData", []).append(tb)
        strings = {}
        for cp in tb.get("TireCompounds") or []:
            n = cp.get("Name")
            if isinstance(n, dict) and n.get("table") and not strings:
                strings = read_string_table(content, n["table"].split(".")[0])
        name = "%s%s.tbc" % (car, "" if i == 0 else "_%d" % i)
        txt, tgms = write_tbc(tb, car, strings)
        with open(os.path.join(out_dir, name), "w", encoding="utf-8") as fh:
            fh.write(txt)
        if i == 0:
            files["tbc"] = name
        for adv in tgms:
            fn = "%s.tgm" % adv["name"]
            if fn in written_tgm:
                continue
            written_tgm.add(fn)
            try:
                txt, err = build_tgm(content, adv, adv["name"])
            except Exception as ex:          # noqa
                txt, err = None, str(ex)
            if txt:
                with open(os.path.join(out_dir, fn), "w", encoding="utf-8") as fh:
                    fh.write(txt)
                log("  TGM geschrieben: %s" % fn)
            else:
                log("  [!] TGM %s nicht erstellt: %s" % (fn, err))
    # HDV
    with open(os.path.join(out_dir, "%s.hdv" % car), "w", encoding="utf-8") as fh:
        fh.write(write_hdv(phys, car, files))
    if dump_json:
        with open(os.path.join(out_dir, "%s_rennsport.json" % car), "w", encoding="utf-8") as fh:
            json.dump(dump, fh, indent=1, default=str)
    written = sorted(f for f in os.listdir(out_dir) if f.startswith(car) or f.endswith(".tgm"))
    for f in written:
        log("  -> %s" % os.path.join(out_dir, f))


# ===========================================================================
#  Main
# ===========================================================================
def _norm_content(p):
    if not p:
        return None
    p = os.path.abspath(p.strip().strip('"'))
    for cand in (p, os.path.join(p, "Content"), os.path.join(p, "Rennsport", "Content")):
        if os.path.isdir(os.path.join(cand, "Blueprints")):
            return cand
    return None


def main():
    ap = argparse.ArgumentParser(description="Rennsport-Physik -> rFactor 2")
    ap.add_argument("cars", nargs="*", help="Config-Ordner oder Name, z.B. BMW_M4_GT3_2022")
    ap.add_argument("-o", "--output", default="rF2_Export", help="Ausgabeordner")
    ap.add_argument("--content", help="Content-Ordner der entpackten PAK")
    ap.add_argument("--list", action="store_true", help="verfuegbare Fahrzeuge anzeigen")
    ap.add_argument("--all", action="store_true", help="alle Fahrzeuge konvertieren")
    ap.add_argument("--json", action="store_true", help="zusaetzlich kompletten JSON-Dump schreiben")
    args = ap.parse_args()

    cfg = configparser.ConfigParser()
    if os.path.isfile(INI_PATH):
        cfg.read(INI_PATH, encoding="utf-8")
    if not cfg.has_section("Paths"):
        cfg.add_section("Paths")

    content = _norm_content(args.content)
    if not content:
        for a in args.cars:
            if os.path.isdir(a.strip('"')):
                content = content_from_car_dir(a.strip('"'))
                break
    if not content:
        content = _norm_content(cfg.get("Paths", "content", fallback=""))
    while not content:
        try:
            p = input("Pfad zum entpackten Ordner (z.B. ...\\Rennsport-Windows_extracted): ")
        except (EOFError, KeyboardInterrupt):
            sys.exit("\nAbgebrochen.")
        content = _norm_content(p)
        if not content:
            print("  Dort gibt es keinen 'Blueprints'-Ordner.")
    if cfg.get("Paths", "content", fallback="") != content:
        cfg.set("Paths", "content", content)
        with open(INI_PATH, "w", encoding="utf-8") as fh:
            cfg.write(fh)

    if args.all:
        args.cars = sorted(find_car_dirs(content))
    if args.list or not args.cars:
        cars = sorted(find_car_dirs(content))
        print("Verfuegbare Fahrzeuge (%d):" % len(cars))
        for c in cars:
            print("  " + c)
        if not args.cars:
            return
    out = os.path.abspath(args.output)
    for a in args.cars:
        d = resolve_car(content, a)
        if not d:
            log("[!] Fahrzeug '%s' nicht gefunden (--list zeigt alle)" % a)
            continue
        try:
            convert(content, d, os.path.join(out, os.path.basename(d)), args.json)
        except Exception as ex:
            import traceback
            log("[FEHLER] %s: %s\n%s" % (a, ex, traceback.format_exc()))


if __name__ == "__main__":
    main()
