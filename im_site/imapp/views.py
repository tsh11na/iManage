from django.views import generic
from django.http import HttpResponse, HttpResponseRedirect
from .models import ModelInfo, Equipment, User, PcEquipment, Log
from django.db import connection
from django.template import loader
from collections import defaultdict
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import Http404
from django.urls import reverse

NOT_ASSIGNED_ID = 1
TO_BE_SCRAPPED_ID = 2
SCRAPPED_ID = 3

ID_MODE = {NOT_ASSIGNED_ID, TO_BE_SCRAPPED_ID, SCRAPPED_ID}


class RegisterBaseInfo:
    def __init__(self, username, userid, year, desktop, laptop, displays):
        self.username = username
        self.userid = userid
        self.assignedyear = year
        self.desktop = desktop
        self.laptop = laptop
        self.displays = displays

    def __str__(self):
        return "in RegisterBaseInfo class(debug on __str__): " + str(self.username) + ", " + str(
            self.userid) + ", " + str(self.desktop) + ", " + str(self.laptop) + ", " + str(self.displays)


class register(generic.ListView):
    """
    in registering user&sam to log
    """
    template_name = 'imapp/register.html'

    NO_DEFAULT_SAM = "該当なし"
    DISPOSAL_ID = [TO_BE_SCRAPPED_ID, SCRAPPED_ID]  # disposal or will dispose
    # not assigned or disposal or will dispose
    NO_USE_ID = [NOT_ASSIGNED_ID, TO_BE_SCRAPPED_ID, SCRAPPED_ID]

    def __init__(self):
        self.SendContentsSave = []

    def GetValidSamAndUsersSam(self, SendContents, DesktopSamTable, LaptopSamTable, DisplaySamTable):
        """
        Requirement: A and B don't exist such as A.sam == B.sum ∧ A.begin_date == B.begin_date is in LOG
        {users}, {user-desktop-sam, {vaild-desktop-sam}}, 
        {user-laptop-sam, {vaild-laptop-sam}}, {user-displaysam1/2, {valid-display-sam}}

        """
        cursor = connection.cursor()
        cursor.execute("""SELECT sam_id,user_id_id FROM (SELECT A.sam_id, 
        A.user_id_id FROM imapp_log AS A INNER JOIN 
        (SELECT sam_id, MAX(begin_date) AS MaxDate 
        FROM `imapp_log` GROUP BY sam_id) AS B
        ON A.sam_id = B.sam_id AND A.begin_date = B.MaxDate ) as C 
        INNER JOIN imapp_user ON C.user_id_id = imapp_user.user_id""")
        sam_userid_rows = cursor.fetchall()

        # No valid ID
        NoValidSumTable = []
        userid_sam_dfdict = defaultdict(list)
        for sam, userid in sam_userid_rows:
            if userid not in self.DISPOSAL_ID:
                userid_sam_dfdict[userid].append(sam)
            else:
                NoValidSumTable.append(sam)

        # display valid ID
        DisplaySamTable.clear()

        for dic in Equipment.objects.all().filter(pc_or_display="display").values():
            if dic["sam"] not in NoValidSumTable:
                DisplaySamTable.append(dic["sam"])
        DisplaySamTable.append(self.NO_DEFAULT_SAM)

        # Desktop valid ID
        DesktopSamTable.clear()

        desktop_dicts = ModelInfo.objects.all().filter(desk_or_lap="desktop").values()
        desktop_model_ids = [id_dict['model_id'] for id_dict in desktop_dicts]

        for equip in Equipment.objects.all().values():
            if equip["model_id_id"] in desktop_model_ids:
                if equip["sam"] not in NoValidSumTable:
                    DesktopSamTable.append(equip["sam"])
        DesktopSamTable.append(self.NO_DEFAULT_SAM)

        # Laptop valid ID
        LaptopSamTable.clear()

        laptop_dicts = ModelInfo.objects.all().filter(desk_or_lap="laptop").values()
        laptop_model_ids = [id_dict['model_id'] for id_dict in laptop_dicts]

        for equip in Equipment.objects.all().values():
            if equip["model_id_id"] in laptop_model_ids:
                if equip["sam"] not in NoValidSumTable:
                    LaptopSamTable.append(equip["sam"])
        LaptopSamTable.append(self.NO_DEFAULT_SAM)

        userid_sam_dict = dict(userid_sam_dfdict)  # defaultdict to dict

        SendContents.clear()
        for userdata in User.objects.all().values():
            username = userdata["username"]
            userid = userdata["user_id"]
            user_assignedyeser = userdata["assigned_year"]
            if userid in self.NO_USE_ID:
                continue
            if userdata["is_affiliated"] == False:
                continue

            UserSamSet = []
            if userid in userid_sam_dict.keys():
                UserSamSet = userid_sam_dict[userid]

            desktopsam = ""  # if cond assignment
            laptopsam = ""
            displaysams = []
            for sam in UserSamSet:
                if sam in DesktopSamTable:
                    desktopsam = sam
                elif sam in LaptopSamTable:
                    laptopsam = sam
                elif sam in DisplaySamTable:
                    displaysams.append(sam)

            # if a person doesn't have sam -> person.sth.sam=NO_DEFAULT_SAM
            if len(desktopsam) < 1:
                desktopsam = self.NO_DEFAULT_SAM
            if len(laptopsam) < 1:
                laptopsam = self.NO_DEFAULT_SAM
            for i in range(2 - len(displaysams)):
                displaysams.append(self.NO_DEFAULT_SAM)
            SendContents.append(RegisterBaseInfo(
                username, userid, user_assignedyeser, desktopsam, laptopsam, displaysams))

    def validsetting(self):
        pass

    def post(self, request, *args, **kwargs):

        post_data = request.POST

        post_id = int(post_data["userid"])
        d =  post_data["desktop-pulldown"]
        l =  post_data["laptop-pulldown"]
        d1 = post_data["display1-pulldown"]
        d2 = post_data["display2-pulldown"]


        # get pre information
        SendContents = []
        DesktopSamTable = []
        LapTopSamTable = []
        DisplaySamTable = []
        self.GetValidSamAndUsersSam(SendContents, DesktopSamTable,
                              LapTopSamTable, DisplaySamTable)


        # get who change sam
        postinfo = RegisterBaseInfo("", post_id, 0, d, l, [d1, d2])
        preinfo = postinfo
        for pre in SendContents:
            if pre.userid == post_id:
                preinfo = pre

        # get pre/change infomation ↓
        predisp1 = preinfo.displays[0]
        predisp2 = preinfo.displays[1]

        # desktop
        class OldAndNew():
            def __init__(self, oldsam, newsam):
                self.newsam = newsam
                self.oldsam = oldsam

        checksams = []
        if preinfo.desktop != postinfo.desktop:
            checksams.append(OldAndNew(preinfo.desktop, postinfo.desktop))

        # laptop
        if preinfo.laptop != postinfo.laptop:
            checksams.append(OldAndNew(preinfo.laptop, postinfo.laptop))

        # display: 2displays -> check algorithm
        deletelist_old = []
        deletelist_new = []
        boolenlist_old = [False for a in preinfo.displays]
        boolenlist_new = [False for a in postinfo.displays]
        for i, newsam in enumerate(postinfo.displays):
            for j, oldsam in enumerate(preinfo.displays):
                if boolenlist_new[i] == False and boolenlist_old[j] == False and newsam == oldsam:
                    deletelist_old.append(oldsam)
                    deletelist_new.append(newsam)
                    boolenlist_old[j] = True
                    boolenlist_new[i] = True

        for oldsam in deletelist_old:
            preinfo.displays.remove(oldsam)
        for newsam in deletelist_new:
            postinfo.displays.remove(newsam)

        assert len(postinfo.displays) == len(
            preinfo.displays), "the size of preinfo.displays is not postinfo.displays, ><"
        for (oldsam, newsam) in zip(preinfo.displays, postinfo.displays):
            checksams.append(OldAndNew(oldsam, newsam))


        """
        old sam -> no_assinnment
        new sam -> person
        """
        ## old sam to LOG
        # if same sam and begin_date in LOG, delete it
        for obj in checksams:
            oldsam = obj.oldsam
            Logsset = Log.objects.all().filter(sam=oldsam, begin_date=datetime.now())
            # if nothing is target, none happens
            Logsset.delete()

        for obj in checksams:
            if obj.oldsam == self.NO_DEFAULT_SAM:
                continue
            insert_query = Log(
                sam=Equipment.objects.get(sam=obj.oldsam),
                begin_date=datetime.now(),
                user_id=User.objects.get(user_id=NOT_ASSIGNED_ID)
            )
            insert_query.save()


        # delete same date and sam
        for obj in checksams:
            if obj.newsam == self.NO_DEFAULT_SAM:
                continue
            newsam = obj.newsam
            Logsset = Log.objects.all().filter(sam=newsam, begin_date=datetime.now())
            Logsset.delete() # if nothing is target, none happens

        # new data to LOG
        for obj in checksams:
            if obj.newsam == self.NO_DEFAULT_SAM:
                continue
            insert_query = Log(
                sam=Equipment.objects.get(sam=obj.newsam),
                begin_date=datetime.now(),
                user_id=User.objects.get(user_id=postinfo.userid)
            )
            insert_query.save()

        class SamChangeInfo:  # insert only diff data
            def __init__(self, id, de, l, d1, d2, change=False, deskch=False, lapch=False, dispch=False):
                self.id = id
                self.desktop = de
                self.laptop = l
                self.display = [d1, d2]
                self.change = change
                self.desktopchange = deskch
                self.laptopchange = lapch
                self.displaychange = dispch

        # diff check(worst...)
        cnt = 0
        chflag = False
        deskflag = False
        lapflag = False
        dispflag = False
        if preinfo.desktop == postinfo.desktop:
            cnt += 1
        else:
            deskflag = True
        if preinfo.laptop == postinfo.laptop:
            cnt += 1
        else:
            lapflag = True
        if preinfo.displays == postinfo.displays:
            cnt += 1
        else:
            dispflag = True

        if deskflag or lapflag or dispflag:
            chflag = True
        return self.get(no_use='no_use',
                        Diff=SamChangeInfo(post_id, d, l, d1, d2, chflag, deskflag, lapflag, dispflag),
                        Pre=SamChangeInfo(preinfo.userid, preinfo.desktop, preinfo.laptop, predisp1, predisp2, chflag, deskflag,
                                lapflag, dispflag))

    def get(self, no_use='no_use', Diff=None, Pre=None, *args, **kwargs):
        SendContents = []
        DesktopSamTable = []
        LapTopSamTable = []
        DisplaySamTable = []
        self.GetValidSamAndUsersSam(SendContents, DesktopSamTable,
                              LapTopSamTable, DisplaySamTable)

        self.object_list = self.get_queryset()

        context = {
            'context_infos': SendContents,
            'desktop_sams': DesktopSamTable,
            'laptop_sams': LapTopSamTable,
            'display_sams': DisplaySamTable,
            'diff': Diff,
            'pre': Pre,
        }
        return self.render_to_response(context)

    def get_queryset(self):
        return

class IndexView(generic.ListView):
    template_name = 'imapp/index.html'

    def get_queryset(self):
        return


class LogView(generic.ListView):
    model = Log
    template_name = 'imapp/log.html'

    NO_DEFAULT_SAM = "該当なし"
    DISPOSAL_ID = [TO_BE_SCRAPPED_ID, SCRAPPED_ID]  # disposal or will dispose
    # not assigned or disposal or will dispose
    NO_USE_ID = [NOT_ASSIGNED_ID, TO_BE_SCRAPPED_ID, SCRAPPED_ID]

    def GetValidTypeList(self, DesktopSamTable, LaptopSamTable, DisplaySamTable, baseTime):
        cursor = connection.cursor()
        cursor.execute(f"""SELECT sam_id, user_id_id FROM 
                    (SELECT A.sam_id, A.user_id_id FROM imapp_log AS A
                        INNER JOIN (SELECT D.sam_id, MAX(D.begin_date) AS MaxDate
                     FROM (SELECT sam_id, begin_date FROM imapp_log WHERE begin_date <= \'{baseTime}\' ) AS D
                    GROUP BY D.sam_id) AS B ON A.sam_id = B.sam_id  AND A.begin_date = B.MaxDate
                    )as C INNER JOIN imapp_user ON C.user_id_id = imapp_user.user_id """)
        sam_userid_rows = cursor.fetchall()

        # delete No valid ID(scrap/will dispose)
        NoValidSumTable = []
        userid_sam_dfdict = defaultdict(list)
        for sam, userid in sam_userid_rows:
            if userid not in self.DISPOSAL_ID:
                userid_sam_dfdict[userid].append(sam)
            else:
                NoValidSumTable.append(sam)

        # display valid ID
        DisplaySamTable.clear()
        for dic in Equipment.objects.all().filter(pc_or_display="display").values():
            if dic["sam"] not in NoValidSumTable:
                DisplaySamTable.append(dic["sam"])

        # Desktop valid ID
        DesktopSamTable.clear()

        desktop_dicts = ModelInfo.objects.all().filter(desk_or_lap="desktop").values()
        desktop_model_ids = [id_dict['model_id'] for id_dict in desktop_dicts]

        for equip in Equipment.objects.all().values():
            if equip["model_id_id"] in desktop_model_ids:
                if equip["sam"] not in NoValidSumTable:
                    DesktopSamTable.append(equip["sam"])

        # Laptop valid ID
        LaptopSamTable.clear()

        laptop_dicts = ModelInfo.objects.all().filter(desk_or_lap="laptop").values()
        laptop_model_ids = [id_dict['model_id'] for id_dict in laptop_dicts]

        for equip in Equipment.objects.all().values():
            if equip["model_id_id"] in laptop_model_ids:
                if equip["sam"] not in NoValidSumTable:
                    LaptopSamTable.append(equip["sam"])

    def post(self, request, *args, **kwargs):
        post_data = request.POST
        select_time = post_data["select_time"]

        currentdate = datetime.now()
        selectdate = datetime.strptime(select_time, "%Y-%m-%d")
        if selectdate > currentdate:
            selectdate = currentdate

        return self.get(no_use='no_use', CurTime=selectdate)

    def get(self, no_use='no_use', CurTime=datetime.now(), *args, **kwargs):
        self.object_list = self.get_queryset()
        baseTime = CurTime.strftime("%Y%m%d")
        cursor = connection.cursor()
        cursor.execute(f"""
        SELECT sam_id, username FROM (SELECT A.sam_id, A.user_id_id FROM imapp_log AS A
        INNER JOIN (SELECT D.sam_id, MAX(D.begin_date) AS MaxDate FROM
        (SELECT sam_id, begin_date FROM imapp_log WHERE begin_date <= \'{baseTime}\'
        ) AS D GROUP BY D.sam_id) AS B ON A.sam_id = B.sam_id AND A.begin_date = B.MaxDate
        )as C INNER JOIN imapp_user ON C.user_id_id = imapp_user.user_id """)

        sam_user_rows = cursor.fetchall()
        sam_and_users = [list(sam_user) for sam_user in list(sam_user_rows)]
        saminfo = Equipment.objects.all()
        modelinfo = ModelInfo.objects.all()

        desktop_valid_sams = []
        laptop_valid_sams = []
        display_valid_sams = []
        self.GetValidTypeList(desktop_valid_sams,
                              laptop_valid_sams, display_valid_sams, baseTime)
        output = []

        for a in sam_and_users:
            """
            tableobj(for html) : [sam_id, username, (equipment), (model_info), linktxt, cpu,os,drive]
            """
            tableobj = []
            tableobj.append(a[0])  # sam_id
            tableobj.append(a[1])  # username

            equipment_info = saminfo.filter(sam=a[0]).values()[0]
            tableobj.append(equipment_info)

            model_info_info = modelinfo.filter(
                model_id=equipment_info["model_id_id"]).values()[0]
            tableobj.append(model_info_info)

            linktxt = "%sの使用履歴" % a[0]
            tableobj.append(linktxt)
            if (a[0] in desktop_valid_sams) or (a[0] in laptop_valid_sams):
                os_cpu_drive_memory_info = PcEquipment.objects.all().filter(sam=a[0])
                tableobj.append(os_cpu_drive_memory_info[0].os_id.os)
                tableobj.append(os_cpu_drive_memory_info[0].cpu_id.cpu)
                tableobj.append(os_cpu_drive_memory_info[0].drive_id.drive)
                tableobj.append(os_cpu_drive_memory_info[0].memory_id.memory)
            elif a[0] in display_valid_sams:
                display_table = Equipment.objects.all().filter(sam=a[0])
                inch_info = display_table[0].model_id.related_model_id.inch
                tableobj.append(inch_info)
            output.append(tableobj)

        template = loader.get_template('imapp/log.html')
        context = {
            'sam_user_rows': output,
            'CurTime': CurTime.date(),
            'desktop_valid_sams': desktop_valid_sams,
            'laptop_valid_sams': laptop_valid_sams,
            'display_valid_sams': display_valid_sams,
        }
        return self.render_to_response(context)

    def get_queryset(self):
        return


def loglog(request, sam_site):
    """
    make tables about one sam_id [begin_date, username]
    """

    cursor = connection.cursor()
    cursor.execute(f"""SELECT begin_date, username FROM imapp_log, imapp_user
                WHERE imapp_log.user_id_id = imapp_user.user_id and imapp_log.sam_id = \'{sam_site}\'""")

    date_user_rows = cursor.fetchall()

    date_and_users = [list(date_user) for date_user in list(date_user_rows)]
    output = date_and_users

    template = loader.get_template('imapp/loglog.html')
    context = {
        'date_user_rows': output,
        'sam_site': sam_site,
    }

    return HttpResponse(template.render(context, request))


class scLogView(generic.ListView):
    model = Log
    template_name = 'imapp/sclog.html'

    NO_DEFAULT_SAM = "該当なし"
    DISPOSAL_ID = [TO_BE_SCRAPPED_ID, SCRAPPED_ID]  # disposal or will dispose
    # not assigned or disposal or will dispose
    NO_USE_ID = [NOT_ASSIGNED_ID, TO_BE_SCRAPPED_ID, SCRAPPED_ID]

    # scrap/to scrap only
    def GetValidTypeList(self, DesktopSamTable, LaptopSamTable, DisplaySamTable, baseTime):
        cursor = connection.cursor()
        cursor.execute(f"""
        SELECT sam_id, user_id_id FROM (SELECT A.sam_id, A.user_id_id FROM imapp_log AS A
        INNER JOIN (SELECT D.sam_id, MAX(D.begin_date) AS MaxDate FROM ( SELECT 
        sam_id, begin_date FROM imapp_log WHERE begin_date <= \'{baseTime}\') AS D
        GROUP BY D.sam_id) AS B ON A.sam_id = B.sam_id AND A.begin_date = B.MaxDate
        )as C INNER JOIN imapp_user ON C.user_id_id = imapp_user.user_id """)
        sam_userid_rows = cursor.fetchall()
        print("IN function , ", sam_userid_rows)
        ValidSamTable = []  # !caution! this list includes validid
        userid_sam_dfdict = defaultdict(list)
        for sam, userid in sam_userid_rows:
            if userid not in self.DISPOSAL_ID:
                ValidSamTable.append(sam)

        # display valid ID
        DisplaySamTable.clear()
        for dic in Equipment.objects.all().filter(pc_or_display="display").values():
            if dic["sam"] not in ValidSamTable:
                DisplaySamTable.append(dic["sam"])

        # Desktop valid ID
        DesktopSamTable.clear()

        desktop_dicts = ModelInfo.objects.all().filter(desk_or_lap="desktop").values()
        desktop_model_ids = [id_dict['model_id'] for id_dict in desktop_dicts]

        for equip in Equipment.objects.all().values():
            if equip["model_id_id"] in desktop_model_ids and equip["sam"] not in ValidSamTable:
                # Laptop valid ID
                DesktopSamTable.append(equip["sam"])

        # Laptop valid ID
        LaptopSamTable.clear()

        laptop_dicts = ModelInfo.objects.all().filter(desk_or_lap="laptop").values()
        laptop_model_ids = [id_dict['model_id'] for id_dict in laptop_dicts]

        for equip in Equipment.objects.all().values():
            if equip["model_id_id"] in laptop_model_ids and equip["sam"] not in ValidSamTable:
                LaptopSamTable.append(equip["sam"])

    def post(self, request, *args, **kwargs):

        post_data = request.POST
        select_time = post_data["select_time"]
        currentdate = datetime.now()
        selectdate = datetime.strptime(select_time, "%Y-%m-%d")
        if selectdate > currentdate:
            selectdate = currentdate

        return self.get(no_use='no_use', CurTime=selectdate)

    def get(self, no_use='no_use', CurTime=datetime.now(), *args, **kwargs):
        self.object_list = self.get_queryset()
        baseTime = CurTime.strftime("%Y%m%d")
        cursor = connection.cursor()
        cursor.execute(f"""
        SELECT sam_id, username FROM (SELECT A.sam_id, A.user_id_id FROM imapp_log AS A
        INNER JOIN (SELECT D.sam_id, MAX(D.begin_date) AS MaxDate FROM ( SELECT 
        sam_id, begin_date FROM imapp_log WHERE begin_date <= \'{baseTime}\') AS D
        GROUP BY D.sam_id) AS B ON A.sam_id = B.sam_id AND A.begin_date = B.MaxDate)as C 
        INNER JOIN imapp_user ON C.user_id_id = imapp_user.user_id """)

        sam_user_rows = cursor.fetchall()
        sam_and_users = [list(sam_user) for sam_user in list(sam_user_rows)]
        saminfo = Equipment.objects.all()
        modelinfo = ModelInfo.objects.all()

        desktop_valid_sams = []
        laptop_valid_sams = []
        display_valid_sams = []
        self.GetValidTypeList(desktop_valid_sams,
                              laptop_valid_sams, display_valid_sams, baseTime)
        output = []

        for a in sam_and_users:
            """
            tableobj : [sam_id, username, (equipment), (model_info), linktxt]
            """
            tableobj = []
            tableobj.append(a[0])  # sam_id
            tableobj.append(a[1])  # username

            equipment_info = saminfo.filter(sam=a[0]).values()[0]
            tableobj.append(equipment_info)

            model_info_info = modelinfo.filter(
                model_id=equipment_info["model_id_id"]).values()[0]
            tableobj.append(model_info_info)

            linktxt = "%sの使用履歴" % a[0]
            tableobj.append(linktxt)

            if (a[0] in desktop_valid_sams) or (a[0] in laptop_valid_sams):
                os_cpu_drive_memory_info = PcEquipment.objects.all().filter(sam=a[0])
                tableobj.append(os_cpu_drive_memory_info[0].os_id.os)
                tableobj.append(os_cpu_drive_memory_info[0].cpu_id.cpu)
                tableobj.append(os_cpu_drive_memory_info[0].drive_id.drive)
                tableobj.append(os_cpu_drive_memory_info[0].memory_id.memory)
            elif a[0] in display_valid_sams:
                display_table = Equipment.objects.all().filter(sam=a[0])
                inch_info = display_table[0].model_id.related_model_id.inch
                tableobj.append(inch_info)

            output.append(tableobj)

        templates = loader.get_template('imapp/sclog.html')
        context = {
            'sam_user_rows': output,
            'CurTime': CurTime.date(),
            'desktop_valid_sams': desktop_valid_sams,
            'laptop_valid_sams': laptop_valid_sams,
            'display_valid_sams': display_valid_sams,
        }
        return self.render_to_response(context)

    def get_queryset(self):
        return


class UnregisterIndexView(generic.View):

    def get(self, request, mode_id, *args, **kwargs):

        USER_SCRAPPABLE = User.objects.get(user_id=TO_BE_SCRAPPED_ID)
        USER_SCRAPPED = User.objects.get(user_id=SCRAPPED_ID)

        # Userが一般の場合は例外処理
        if mode_id not in ID_MODE:
            raise Http404
        mode_user = get_user_from_id(mode_id)
        context = {
            'mode_id': mode_id,
            'mode_name': mode_user.username,
        }

        # 変更された備品のSAMがあればcontextに追加
        if 'changed' in request.GET:
            context['changed'] = request.GET['changed']

        # 廃棄にする場合は廃棄予定のみ抽出
        if mode_user == USER_SCRAPPED:
            log_set = fetch_latest_logs_used_by(USER_SCRAPPABLE)
        # 未割当・廃棄予定にする場合は「自分or廃棄」以外をすべて抽出
        else:
            log_set = \
                fetch_latest_logs() \
                - fetch_latest_logs_used_by(mode_user) \
                - fetch_latest_logs_used_by(USER_SCRAPPED)

        log_set_desktop = filter_logs_of(log_set, 'desktop')
        log_set_laptop = filter_logs_of(log_set, 'laptop')
        log_set_display = filter_logs_of(log_set, 'display')

        # SAMのsetを取得し、リストに変換して並び替え
        sams_of_desktop = to_list_and_sort(fetch_value_from_model_obj(log_set_desktop, 'sam_id'))
        sams_of_laptop = to_list_and_sort(fetch_value_from_model_obj(log_set_laptop, 'sam_id'))
        sams_of_display = to_list_and_sort(fetch_value_from_model_obj(log_set_display, 'sam_id'))

        context['sams_of_desktop'] = sams_of_desktop
        context['sams_of_laptop'] = sams_of_laptop
        context['sams_of_display'] = sams_of_display

        # 選択できるSAMがある場合
        if context['sams_of_desktop'] or context['sams_of_laptop'] or context['sams_of_display']:
            return render(request, 'imapp/unregister/index.html', context)
        # 選択できるSAMがない場合
        else:
            return render(request, 'imapp/unregister/no_sam.html', context)


class UnregisterConfirmView(generic.View):

    def post(self, request, mode_id):
        # Userが一般の場合は例外処理
        if mode_id not in ID_MODE:
            raise Http404
        sam = request.POST['sam']
        equipment = Equipment.objects.get(sam=sam)
        model = ModelInfo.objects.get(model_id=equipment.model_id_id)
        latest_log = Log.objects.filter(sam_id=sam).latest('begin_date')
        user = User.objects.get(user_id=latest_log.user_id_id)
        context = {
            'mode_id': mode_id,
            'mode_name': get_user_from_id(mode_id).username,
            'equipment': equipment,
            'model': model,
            'user': user
        }
        return render(request, 'imapp/unregister/confirm.html', context)


def run_unregister(request, mode_id):
    """DBの更新"""

    sam = request.POST['sam']

    # SAMが同じで、今日の日付のログがあれば削除
    logs_today = Log.objects.filter(sam=sam, begin_date=datetime.now())
    logs_today.delete()

    # ログを保存
    query = Log(
        begin_date=datetime.now(),
        sam_id=Equipment.objects.get(sam=sam),
        user_id_id=mode_id
    )
    query.save()

    # GETパラメータに変更された備品のSAMを追加
    response = redirect('imapp:unregister_index', mode_id=mode_id)
    response['location'] += '?changed=' + sam
    return response


def get_user_from_id(user_id):
    return User.objects.get(user_id=user_id)


def get_log(sam):
    """指定されたSAMのログのQuerysetを返す"""
    return Log.objects.filter(sam_id=sam)


def get_latest_log(sam):
    """指定されたSAMの最新のログを返す"""
    return get_log(sam).latest('begin_date')


def fetch_latest_logs():
    """SAMごとの最新のログを収集し、setにして返す"""
    # ログにあるSAMのリストを取得
    sams = Log.objects.all().values_list('sam_id', flat=True).order_by('sam_id').distinct()
    latest_logs = set()
    for sam in sams:
        latest_log = get_latest_log(sam)
        latest_logs.add(latest_log)
    return latest_logs


def fetch_latest_logs_used_by(user):
    """特定のユーザが使っている備品のログを収集し、setにして返す"""
    latest_logs = fetch_latest_logs()
    latest_logs_fetched = set()
    # 各備品の最新のログについて
    for latest_log in latest_logs:
        # ユーザを取得し、
        current_user = getattr(latest_log, 'user_id')
        # 指定されたユーザが使っていればsetに追加
        if current_user == user:
            latest_logs_fetched.add(latest_log)
    return latest_logs_fetched


def fetch_value_from_model_obj(model_obj_set: set, field: str):
    """モデルオブジェクトインスタンスsetの特定のフィールド値を取得し、setにして返す"""
    value_set = set()
    for model_obj in model_obj_set:
        value_set.add(getattr(model_obj, field))
    return value_set


def filter_logs_of(latest_logs: set, category: str):
    """categoryに指定したdesktop/laptop/displayのlogのsetを返す"""
    filtered_logs = set()
    # それぞれのLogについて、
    for log in latest_logs:
        # モデルIDを取得し、
        sam = getattr(log, 'sam_id')
        model_id = getattr(Equipment.objects.get(sam=sam), 'model_id_id')
        # カテゴリが合致すれば追加
        model = ModelInfo.objects.get(model_id=model_id)
        category_of_log = getattr(model, 'desk_or_lap') or getattr(model, 'pc_or_display')
        if category_of_log == category:
            filtered_logs.add(log)
    return filtered_logs


def to_list_and_sort(my_set: set):
    """setをlistにしてソートする"""
    my_list = list(my_set)
    return sorted(my_list)