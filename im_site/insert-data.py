from django.db import models
from django.utils import timezone
import datetime
# -*- coding: utf-8 -*-
"""
Insert Data to DB
for user, log, equipment, pc_equipment
"""
import django
django.setup()
from imapp.models import (
    ModelInfo,
    DisplayInfo,
    Equipment,
    OsId,
    CpuId,
    DriveId,
    MemoryId,
    PcEquipment,
    User,
    Log,
)


os_ids = [
    'windows10 64bit',
    'windows7 32bit',
    'windows7 64bit',
]
for row in os_ids:
    insert_query = OsId(os=row)
    insert_query.save()

cpu_ids = [
    'core i7-5700',
    'core i5-4500',
    'core i9-9000',
]
for row in cpu_ids:
    insert_query = CpuId(cpu=row)
    insert_query.save()

drive_ids = [
    'HDD 500GB',
    'SSD 256GB',
    'HDD 500GB + SSD 128GB',
]
for row in drive_ids:
    insert_query = DriveId(drive=row)
    insert_query.save()

memory_ids = [
    '2GB',
    '4GB',
    '8GB',
    '16GB',
]
for memory_id in memory_ids:
    insert_query = MemoryId(memory=memory_id)
    insert_query.save()

model_infos = [
    ["pc", "desktop", "OPTIPLEX", "DELL", 20120101],
    ["pc", "laptop", "Let's note CX4", "Panasonic", 20130405],
    ["pc", "laptop", "Let's note SX5", "Panasonic", 20140502],
    ["display", "", "U2412", "DELL", 20121101],
    ["display", "", "RDT233", "三菱", 20121130],

    ["display", "", "DELL23", "DELL", 20120101],
    ["display", "", "EIZO15", "EIZO", 20120101],
    ["display", "", "EIZO24", "EIZO", 20120101],
    ["display", "", "BenQ26", "BenQ", 20120101],
    ["display", "", "Sony100", "Sony", 20120101],

    ["pc", "desktop", "TheDesktopPC1", "DELL", 20120101],
    ["pc", "desktop", "TheDesktopPC2", "DELL", 20120101],
    ["pc", "laptop", "TheNotePC1", "Panasonic", 20120101],
    ["pc", "laptop", "TheNotePC2", "Panasonic", 20120101],
]
for row in model_infos:
    insert_query = ModelInfo(
        pc_or_display=row[0],
        desk_or_lap=row[1],
        model_name=row[2],
        maker=row[3],
        release_date=datetime.datetime.strptime(str(row[4]), "%Y%m%d")
    )
    insert_query.save()

display_infos = [
    [4, 24],
    [5, 23],
    [6, 23],
    [7, 15],
    [8, 24],
    [9, 26],
    [10, 100],
]

for m in display_infos:
    a = ModelInfo.objects.get(model_id=m[0])
    insert_query = DisplayInfo(model_id=a, inch=m[1])
    insert_query.save()

equipments = [
    ["DisPlay01 H", "display", 20160414, 20210415, "なし", 6],
    ["DisPlay02 H", "display", 20160414, 20210415, "なし", 6],
    ["DisPlay03 willH", "display", 20160414, 20210415, "なし", 7],
    ["DisPlay04 willH", "display", 20160414, 20210415, "なし", 7],
    ["DisPlay05", "display", 20160414, 20210415, "なし", 8],
    ["DisPlay06", "display", 20160414, 20210415, "なし", 8],
    ["DisPlay07", "display", 20160414, 20210415, "なし", 9],
    ["DisPlay08", "display", 20160414, 20210415, "なし", 9],
    ["DisPlay09", "display", 20160414, 20210415, "なし", 9],
    ["DisPlay10", "display", 20160414, 20210415, "なし", 9],
    ["DisPlay11", "display", 20160414, 20210415, "なし", 10],
    ["DisPlay12", "display", 20160414, 20210415, "なし", 10],

    ["D01", "pc", 20180414, 20210415, "なし", 11],
    ["D02", "pc", 20180414, 20210415, "なし", 12],
    ["D03", "pc", 20180414, 20210415, "なし", 11],
    ["D04", "pc", 20180414, 20210415, "なし", 11],
    ["D05", "pc", 20180414, 20210415, "なし", 11],
    ["D06", "pc", 20180414, 20210415, "なし", 12],
    ["D07", "pc", 20180414, 20210415, "なし", 12],
    ["N01", "pc", 20180414, 20210415, "なし", 13],
    ["N02", "pc", 20180414, 20210415, "なし", 13],
    ["N03", "pc", 20180414, 20210415, "なし", 14],
    ["N04", "pc", 20180414, 20210415, "なし", 14],
    ["N05", "pc", 20180414, 20210415, "なし", 13],
    ["N06", "pc", 20180414, 20210415, "なし", 13],
    ["N07", "pc", 20180414, 20210415, "なし", 14],
]

for eqip in equipments:
    b = ModelInfo.objects.get(model_id=eqip[5])
    insert_query = Equipment(
        sam=eqip[0],
        pc_or_display=eqip[1],
        purchase=datetime.datetime.strptime(str(eqip[2]), "%Y%m%d"),
        warranty=datetime.datetime.strptime(str(eqip[3]), "%Y%m%d"),
        note=eqip[4],
        model_id=b
    )
    insert_query.save()


pc_equipments = [
    ["D01", 1, 2, 3,2],
    ["D02", 1, 1, 3,2],
    ["D03", 2, 3, 1,3],
    ["D04", 2, 2, 1,3],
    ["D05", 3, 1, 3,4],
    ["D06", 3, 2, 2,4],
    ["D07", 3, 2, 2,4],
    ["N01", 2, 3, 1,1],
    ["N02", 2, 2, 1,1],
    ["N03", 1, 1, 3,1],
    ["N04", 1, 2, 2,2],
    ["N05", 3, 3, 2,2],
    ["N06", 3, 1, 3,2],
    ["N07", 3, 2, 3,2],
]

for pceqip in pc_equipments:
    a = Equipment.objects.get(sam=pceqip[0])
    b = OsId.objects.get(os_id=pceqip[1])
    c = CpuId.objects.get(cpu_id=pceqip[2])
    d = DriveId.objects.get(drive_id=pceqip[3])
    m = MemoryId.objects.get(memory_id=pceqip[4])
    insert_query = PcEquipment(
        sam=a,
        os_id=b,
        cpu_id=c,
        drive_id=d,
        memory_id=m
    )
    insert_query.save()


users = [
    ["未割当", 1970, True],   # 1
    ["廃棄予定", 1970, True],  # 2
    ["廃棄", 1970, True],    # 3
    ["石川", 1996, True],  # 4
    ["しいな", 2018, True],    # 5
    ["かさい", 2018, True],    # 6
    ["もりすぎ", 2018, True],   # 7
    ["su川端", 2015, False],    # 8
    ["野田", 2017, True],       # 9
    ["河口", 2013, True],       # 10
    ["おじいさん", 1000, False]  # 11
]


for u in users:
    insert_query = User(username=u[0], assigned_year=u[1])
    insert_query.save()

logs = [
    ["D01", 20160401, 4],
    ["D01", 20170401, 2],
    ["D01", 20180401, 3],
    ["D02", 20160401, 11],
    ["D02", 20170401, 4],
    ["D02", 20180401, 4],
    ["D03", 20160401, 10],
    ["D03", 20170401, 1],
    ["D03", 20180401, 5],
    ["D04", 20160401, 9],
    ["D04", 20170401, 9],
    ["D04", 20180401, 6],
    ["D05", 20160401, 8],
    ["D05", 20170401, 10],
    ["D05", 20180401, 9],
    ["D06", 20160401, 2],
    ["D06", 20170401, 3],
    ["D06", 20180401, 3],
    ["D07", 20160401, 2],
    ["D07", 20170401, 8],
    ["D07", 20180401, 1],
    ["N01", 20161201, 11],
    ["N01", 20171201, 10],
    ["N01", 20180501, 3],
    ["N02", 20161201, 8],
    ["N02", 20171201, 4],
    ["N02", 20180501, 4],
    ["N03", 20161201, 1],
    ["N03", 20171201, 2],
    ["N03", 20180501, 2],
    ["N04", 20161201, 2],
    ["N04", 20171201, 1],
    ["N04", 20180501, 6],
    ["N05", 20161201, 9],
    ["N05", 20171201, 1],
    ["N05", 20180501, 1],
    ["N06", 20161201, 1],
    ["N06", 20171201, 1],
    ["N06", 20180501, 10],
    ["N07", 20161201, 4],
    ["N07", 20171201, 8],
    ["N07", 20180501, 5],

    ["DisPlay01 H", 20160401, 1],
    ["DisPlay01 H", 20170401, 2],
    ["DisPlay01 H", 20180401, 3],

    ["DisPlay02 H", 20160401, 8],
    ["DisPlay02 H", 20170401, 2],
    ["DisPlay02 H", 20180401, 3],

    ["DisPlay03 willH", 20160401, 8],
    ["DisPlay03 willH", 20170401, 9],
    ["DisPlay03 willH", 20180401, 2],

    ["DisPlay04 willH", 20160401, 11],
    ["DisPlay04 willH", 20170401, 9],
    ["DisPlay04 willH", 20180401, 2],

    ["DisPlay05", 20160401, 4],
    ["DisPlay05", 20170401, 4],
    ["DisPlay05", 20180401, 4],

    ["DisPlay06", 20160401, 4],
    ["DisPlay06", 20170401, 4],
    ["DisPlay06", 20180401, 4],

    ["DisPlay07", 20160401, 1],
    ["DisPlay07", 20170401, 1],
    ["DisPlay07", 20180401, 5],

    ["DisPlay08", 20160401, 1],
    ["DisPlay08", 20170401, 1],
    ["DisPlay08", 20180401, 6],

    ["DisPlay09", 20160401, 9],
    ["DisPlay09", 20170401, 10],
    ["DisPlay09", 20180401, 9],

    ["DisPlay10", 20160401, 10],
    ["DisPlay10", 20170401, 10],
    ["DisPlay10", 20180401, 10],

    ["DisPlay11", 20160401, 10],
    ["DisPlay11", 20170401, 1],
    ["DisPlay11", 20180401, 10],

    ["DisPlay12", 20160401, 1],
    ["DisPlay12", 20170401, 1],
    ["DisPlay12", 20180401, 1],
]

for l in logs:

    c = Equipment.objects.get(sam=l[0])
    d = User.objects.get(user_id=l[2])
    insert_query = Log(
        sam=c,
        begin_date=datetime.datetime.strptime(str(l[1]), "%Y%m%d"),
        user_id=d
    )
    insert_query.save()
