from datetime import datetime, timedelta
import time
import config
import pymysql
import pandas as pd
import random as rnd
import prettytable
import winsound


class Utils:
    def connDBSiap(self):
        conn = pymysql.connect(config.db_host_siap,
                               config.db_username_siap,
                               config.db_password_siap,
                               config.db_name_siap)
        return conn

    def getRuangan(self, kecuali, bahasa):
        conn = self.connDBSiap()
        query = "select * from simak_mst_ruangan;"

        with conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            ruangans = []
            for row in rows:
                if row is not None and row[0] is not "-":
                    find = self.findItem(ruangans, row[1])

                    if find:
                        print(find[0])
                        ruangans.pop(find[0])

                    if row[1].lower() in kecuali:
                        continue
                    elif "lab" in row[1].lower():
                        if row[1].lower().replace("lab ", "") in ["318"]:
                            ruangans.append([row[0], row[11], "KOM3"])
                        elif row[1].lower().replace("lab ", "") in ["314", "315"]:
                            ruangans.append([row[0], row[11], "KOM1"])
                        else:
                            ruangans.append([row[0], row[11], "KOM2"])
                    else:
                        if row[0] in bahasa:
                            ruangans.append([row[0], row[11], "BHS"])
                        else:
                            ruangans.append([row[0], row[11], "UMM"])
        return ruangans

    def getWaktuMatkuls(self, menits):
        waktuBB = datetime.strptime("07:00", '%H:%M')
        waktuBTB = datetime.strptime("12:00", '%H:%M')
        waktuBTA = datetime.strptime("13:00", '%H:%M')
        waktuBA = datetime.strptime("18:00", '%H:%M')

        waktuBBDua = datetime.strptime("07:50", '%H:%M')
        waktuBTADua = datetime.strptime("13:50", '%H:%M')

        waktuBBTiga = datetime.strptime("08:40", '%H:%M')
        waktuBTATiga = datetime.strptime("14:40", '%H:%M')

        waktus = []
        kode = 1

        for m in menits:
            waktuAkhir = waktuBB
            putar = 1

            while True:
                waktuAwal = waktuAkhir
                waktuAkhir = waktuAwal+timedelta(minutes=m)

                if putar > 3:
                    break

                if waktuAwal >= waktuBTA:
                    if waktuBTA <= waktuAwal and waktuBA >= waktuAkhir:
                        pukul = waktuAwal.time().strftime("%H:%M")+"-" + \
                            waktuAkhir.time().strftime("%H:%M")
                        waktu = ["W"+str(kode).zfill(2), pukul, m]
                        find = self.findItem(waktus, pukul)
                        if find:
                            continue
                        waktus.append(waktu)
                        kode += 1
                    elif waktuAkhir > waktuBA:
                        if putar == 1:
                            waktuAkhir = waktuBBDua
                        elif putar == 2:
                            waktuAkhir = waktuBBTiga

                        putar += 1
                else:
                    if waktuBB <= waktuAwal and waktuBTB >= waktuAkhir:
                        pukul = waktuAwal.time().strftime("%H:%M")+"-" + \
                            waktuAkhir.time().strftime("%H:%M")
                        waktu = ["W"+str(kode).zfill(2), pukul, m]
                        find = self.findItem(waktus, pukul)
                        if find:
                            continue
                        waktus.append(waktu)
                        kode += 1
                    elif waktuAkhir > waktuBTB:
                        if putar > 1:
                            if putar == 2:
                                waktuAkhir = waktuBTADua
                            elif putar == 3:
                                waktuAkhir = waktuBTATiga
                        else:
                            waktuAkhir = waktuBTA
        return waktus

    def getProdis(self):
        conn = self.connDBSiap()
        query = "SELECT ProdiID, Nama FROM simpati.simak_mst_prodi;"

        with conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            prodis = []
            for row in rows:
                if row is not None:
                    prodis.append([row[0], row[1], []])

        return prodis

    def getMatkuls(self, path):
        df = pd.read_excel(r""+path)
        df = df[df["Perlu Jadwal"] == "Y"]
        kolom = ['SKS', "Perlu Jadwal"]
        df.drop(kolom, axis=1, inplace=True)
        kolom = ["Prodi", "Jumlah Mahasiswa"]
        df[kolom] = df[kolom].applymap(lambda x: '%d' % x)
        kolom = ["Total Jam"]
        df[kolom] = df[kolom].applymap(lambda x: '%d' % (int(x)*50))
        listKode = ["M"+str(x+1).zfill(3) for x in range(0, len(df))]
        df.insert(0, "Kode", listKode, True)
        return df.values.tolist()

    def findItem(self, lists, item):
        return [ind for ind in range(len(lists)) if item in lists[ind]]

    def findListItem(self, lists, item):
        return [lists[ind] for ind in range(len(lists)) if item in lists[ind]]

    def formatWaktu(self, waktu):
        waktu = waktu.replace(" ", "")
        waktus = waktu.split('-')
        awal = datetime.strptime(waktus[0], '%H:%M')
        akhir = datetime.strptime(waktus[1], '%H:%M')
        return [awal, akhir]

    def suaraBeep(self):
        frequency = 2500
        duration = 1000
        for i in range(0, 10):
            winsound.Beep(frequency, duration)


utils = Utils()


class Data:

    HARIS = [["SEN", "Senin"],
             ["SEL", "Selasa"],
             ["RAB", "Rabu"],
             ["KAM", "Kamis"],
             ["JUM", "Jumat"],
             ["SAB", "Sabtu"]]

    RUANGANS = utils.getRuangan(['lab gtz', 'audit 1', '207a', '207b',
                                 'auditorium', 'gor', 'lab bhs', 'lab 306',
                                 'lab 307', 'lab 308'],
                                ["321", "320", "308", "307"])

    WAKTU_MATKULS = utils.getWaktuMatkuls([100, 150, 200, 250, 300])
    PRODIS = utils.getProdis()
    MATKULS = utils.getMatkuls("E:\IRC\MakeJadwal\data.xlsx")

    def __init__(self):
        self._ruangans = []
        self._waktuMatkuls = []
        self._haris = []
        self._prodis = []
        self._matkuls = []

        for i in range(0, len(self.RUANGANS)):
            self._ruangans.append(
                Ruangan(self.RUANGANS[i][0], self.RUANGANS[i][1], self.RUANGANS[i][2]))

        for i in range(0, len(self.WAKTU_MATKULS)):
            self._waktuMatkuls.append(
                WaktuMatkul(self.WAKTU_MATKULS[i][0], self.WAKTU_MATKULS[i][1], self.WAKTU_MATKULS[i][2]))

        for i in range(0, len(self.HARIS)):
            self._haris.append(
                Hari(self.HARIS[i][0], self.HARIS[i][1]))

        for i in range(0, len(self.MATKULS)):
            self._matkuls.append(
                Matkul(self.MATKULS[i][0], self.MATKULS[i][1], self.MATKULS[i][2], self.MATKULS[i][3], self.MATKULS[i][4], self.MATKULS[i]
                       [5], self.MATKULS[i][6], self.MATKULS[i][7], self.MATKULS[i][8], self.MATKULS[i][9], self.MATKULS[i][10])
            )

        for prodi in self.PRODIS:
            matkuls = utils.findListItem(self.MATKULS, prodi[0])
            if matkuls:
                newMatkuls = []
                for matkul in matkuls:
                    newMatkuls.append(Matkul(
                        matkul[0], matkul[1], matkul[2], matkul[3], matkul[4], matkul[5], matkul[6], matkul[7], matkul[8], matkul[9], matkul[10]
                    ))

                self.PRODIS[self.PRODIS.index(prodi)][2].extend(newMatkuls)

        for i in range(0, len(self.PRODIS)):
            if self.PRODIS[i][2]:
                self._prodis.append(
                    Prodi(self.PRODIS[i][0], self.PRODIS[i][1], self.PRODIS[i][2]))

        self._banyakKelas = 0
        for i in range(0, len(self._prodis)):
            self._banyakKelas += len(self._prodis[i].getMatkul())

    def getRuangans(self):
        return self._ruangans

    def getHaris(self):
        return self._haris

    def getMatkuls(self):
        return self._matkuls

    def getProdis(self):
        return self._prodis

    def getWaktuMatkuls(self):
        return self._waktuMatkuls

    def getBanyakKelas(self):
        return self._banyakKelas


class Ruangan:
    def __init__(self, kode, kapasitas, jenis):
        self._kode = kode
        self._kapasitas = kapasitas
        self._jenis = jenis

    def getKode(self):
        return self._kode

    def getKapasitas(self):
        return self._kapasitas

    def getJenis(self):
        return self._jenis


class Hari:
    def __init__(self, kode, nama):
        self._kode = kode
        self._nama = nama

    def getKode(self):
        return self._kode

    def getNama(self):
        return self._nama


class WaktuMatkul:
    def __init__(self, kode, waktu, menit):
        self._kode = kode
        self._waktu = waktu
        self._menit = menit

    def getKode(self):
        return self._kode

    def getWaktu(self):
        return self._waktu

    def getMenit(self):
        return self._menit


class Prodi:
    def __init__(self, kode, nama, matkul):
        self._kode = kode
        self._nama = nama
        self._matkul = matkul

    def getKode(self):
        return self._kode

    def getNama(self):
        return self._nama

    def getMatkul(self):
        return self._matkul


class Matkul:
    def __init__(self, kode, prodi, kodeMatkul, namaMatkul, menit, kelas, kodeDosen, namaDosen, jabatan, jenis, maxMahasiswa):
        self._kode = kode
        self._prodi = prodi
        self._kodeMatkul = kodeMatkul
        self._namaMatkul = namaMatkul
        self._menit = menit
        self._kelas = kelas
        self._kodeDosen = kodeDosen
        self._namaDosen = namaDosen
        self._jabatan = jabatan
        self._jenis = jenis
        self._maxMahasiswa = maxMahasiswa

    def getKode(self):
        return self._kode

    def getProdi(self):
        return self._prodi

    def getKodeMatkul(self):
        return self._kodeMatkul

    def getNamaMatkul(self):
        return self._namaMatkul

    def getMenit(self):
        return self._menit

    def getKelas(self):
        return self._kelas

    def getJabatan(self):
        return self._jabatan

    def getKodeDosen(self):
        return self._kodeDosen

    def getNamaDosen(self):
        return self._namaDosen

    def getJenis(self):
        return self._jenis

    def getMaxMahasiswa(self):
        return self._maxMahasiswa

    def __str__(self):
        return self._kode


class Jadwal:
    def __init__(self, kode, prodi, matkul):
        self._kode = kode
        self._prodi = prodi
        self._matkul = matkul
        self._hari = None
        self._waktuMatkul = None
        self._ruangan = None

    def getKode(self):
        return self._kode

    def getProdi(self):
        return self._prodi

    def getMatkul(self):
        return self._matkul

    def getHari(self):
        return self._hari

    def getWaktuMatkul(self):
        return self._waktuMatkul

    def getRuangan(self):
        return self._ruangan

    def setHari(self, hari):
        self._hari = hari

    def setWaktuMatkul(self, waktuMatkul):
        self._waktuMatkul = waktuMatkul

    def setRuangan(self, ruangan):
        self._ruangan = ruangan

    def __str__(self):
        return self._prodi.getNama()+" | "+self._matkul.getNamaMatkul()+"-"+self._matkul.getKelas() + " | "+self._matkul.getNamaDosen() + " | "+self._ruangan.getKode()+" | "+self._hari.getNama()+" | "+self._waktuMatkul.getWaktu()+" | "+str(self._waktuMatkul.getMenit())+" | "+str(self._matkul.getMenit())


class Penjadwalan:
    def __init__(self):
        self._data = data
        self._jadwal = []
        self._konflik = 0
        self._fitness = -1
        self._kodeJadwal = 0
        self._fitnessBerubah = True

    def getJadwal(self):
        self._fitnessBerubah = True
        return self._jadwal

    def getKonflik(self):
        return self._konflik

    def getFitness(self):
        if(self._fitnessBerubah == True):
            self._fitness = self.hitungFitness()
            self._fitnessBerubah = False
        return self._fitness

    def inisialisasi(self):
        prodis = self._data.getProdis()
        for i in range(0, len(prodis)):
            matkuls = prodis[i].getMatkul()
            for j in range(0, len(matkuls)):
                jadwalBaru = Jadwal(self._kodeJadwal, prodis[i], matkuls[j])
                self._kodeJadwal += 1
                jadwalBaru.setHari(
                    data.getHaris()[rnd.randrange(0, len(data.getHaris()))])
                jadwalBaru.setWaktuMatkul(
                    data.getWaktuMatkuls()[rnd.randrange(0, len(data.getWaktuMatkuls()))])
                jadwalBaru.setRuangan(
                    data.getRuangans()[rnd.randrange(0, len(data.getRuangans()))])
                self._jadwal.append(jadwalBaru)
        return self

    def hitungFitness(self):
        self._konflik = 0
        jadwal = self.getJadwal()
        for i in range(0, len(jadwal)):
            if (int(jadwal[i].getRuangan().getKapasitas()) < int(jadwal[i].getMatkul().getMaxMahasiswa())):
                self._konflik += 1
                # print("max")
                # print(int(jadwal[i].getMatkul().getMaxMahasiswa()))
            ###
            if (str(jadwal[i].getRuangan().getJenis()) != str(jadwal[i].getMatkul().getJenis())):
                self._konflik += 1
                # print("jenis")
                # print(jadwal[i].getMatkul().getJenis())
            ###
            if (int(jadwal[i].getWaktuMatkul().getMenit()) != int(jadwal[i].getMatkul().getMenit())):
                self._konflik += 1
                # print("menit")
                # print(jadwal[i].getMatkul().getMenit())
            ###

            if (jadwal[i].getMatkul().getJabatan().lower() == "y" and jadwal[i].getHari().getNama().lower() == "selasa"):
                self._konflik += 1
                # print("pejabat")
                # print(jadwal[i].getMatkul().getJabatan().lower(), jadwal[i].getHari().getNama().lower())

            waktuSatu = utils.formatWaktu(
                jadwal[i].getWaktuMatkul().getWaktu())

            for j in range(0, len(jadwal)):
                if (j >= i):
                    if jadwal[i].getMatkul().getKodeDosen() == jadwal[j].getMatkul().getKodeDosen() and jadwal[i].getHari().getKode() == jadwal[j].getHari().getKode():
                        waktuDua = utils.formatWaktu(
                            jadwal[j].getWaktuMatkul().getWaktu())
                        if(not(waktuSatu[0] <= waktuDua[0] and waktuSatu[1] <= waktuDua[0] and waktuSatu[0] <= waktuDua[1]) and jadwal[i].getKode() != jadwal[j].getKode()):
                            self._konflik += 1
                            # print("dosen, hari, sama, penentuan waktu")
                            # print(jadwal[i].getMatkul().getKodeDosen(), jadwal[i].getHari().getKode())
                    else:
                        if jadwal[i].getHari().getKode() == jadwal[j].getHari().getKode() and jadwal[i].getRuangan().getKode() == jadwal[j].getRuangan().getKode():
                            waktuDua = utils.formatWaktu(
                                jadwal[j].getWaktuMatkul().getWaktu())
                            if(not(waktuSatu[0] <= waktuDua[0] and waktuSatu[1] <= waktuDua[0] and waktuSatu[0] <= waktuDua[1]) and jadwal[i].getKode() != jadwal[j].getKode()):
                                self._konflik += 1
                                # print("hari, ruangan, sama, penentuan waktu")
                                # print(jadwal[i].getHari().getKode(),jadwal[i].getRuangan().getKode())

        return 1 / ((1.0*self._konflik + 1))

    def __str__(self):
        nilai = ""
        for i in range(0, len(self._jadwal)-1):
            nilai += str(self._jadwal[i])+", "
        nilai += str(self._jadwal[len(self._jadwal)-1])
        return nilai


class Populasi:
    def __init__(self, ukuran):
        self._ukuran = ukuran
        self._data = data
        self._jadwals = []
        for i in range(0, ukuran):
            self._jadwals.append(Penjadwalan().inisialisasi())

    def getJadwals(self):
        return self._jadwals


class AlgoritmaGenetik:
    def evolve(self, populasi):
        return self._mutasiPopulasi(self._crossoverPopulasi(populasi))

    def _crossoverPopulasi(self, pop):
        crossoverPop = Populasi(0)
        for i in range(NOMOR_JADWAL_ELIT):
            crossoverPop.getJadwals().append(pop.getJadwals()[i])
        i = NOMOR_JADWAL_ELIT
        while i < UKURAN_POPULASI:
            jadwalSatu = self._pilihPertandinganPopulasi(pop).getJadwals()[0]
            jadwalDua = self._pilihPertandinganPopulasi(pop).getJadwals()[0]
            crossoverPop.getJadwals().append(self._crossoverJadwal(jadwalSatu, jadwalDua))
            i += 1
        return crossoverPop

    def _mutasiPopulasi(self, populasi):
        for i in range(NOMOR_JADWAL_ELIT, UKURAN_POPULASI):
            self._mutasiJadwal(populasi.getJadwals()[i])
        return populasi

    def _crossoverJadwal(self, jadwalSatu, jadwalDua):
        crossoverJadwal = Penjadwalan().inisialisasi()
        for i in range(0, len(crossoverJadwal.getJadwal())):
            if(rnd.random() > 0.5):
                crossoverJadwal.getJadwal()[i] = jadwalSatu.getJadwal()[i]
            else:
                crossoverJadwal.getJadwal()[i] = jadwalDua.getJadwal()[i]
        return crossoverJadwal

    def _mutasiJadwal(self, mutasiJadwal):
        jadwal = Penjadwalan().inisialisasi()
        for i in range(0, len(mutasiJadwal.getJadwal())):
            if(TINGKAT_MUTASI > rnd.random()):
                mutasiJadwal.getJadwal()[i] = jadwal.getJadwal()[i]
        return mutasiJadwal

    def _pilihPertandinganPopulasi(self, pop):
        pertandinganPop = Populasi(0)
        i = 0
        while i < UKURAN_PERTANDINGAN_TERPILIH:
            pertandinganPop.getJadwals().append(
                pop.getJadwals()[rnd.randrange(0, UKURAN_POPULASI)])
            i += 1
        pertandinganPop.getJadwals().sort(key=lambda x: x.getFitness(), reverse=True)
        return pertandinganPop


class TampilData:
    def tampilDataTersedia(self):
        print("> Semua Data Yang Tersedia")
        self.tampilHari()
        self.tampilRuangan()
        self.tampilWaktuMatkul()
        self.tampilProdi()
        self.tampilMatkul()

    def tampilHari(self):
        tableHari = prettytable.PrettyTable(
            ['Kode', 'Nama'])
        haris = data.getHaris()
        for i in range(0, len(haris)):
            tableHari.add_row(
                [haris[i].getKode(), haris[i].getNama()])
        print(tableHari)

    def tampilRuangan(self):
        tableRuangans = prettytable.PrettyTable(
            ['Kode', 'Kapasitas', 'Jenis'])
        ruangans = data.getRuangans()
        for i in range(0, len(ruangans)):
            tableRuangans.add_row(
                [str(ruangans[i].getKode()), str(ruangans[i].getKapasitas()), str(ruangans[i].getJenis())])
        print(tableRuangans)

    def tampilWaktuMatkul(self):
        tableWaktuMatkuls = prettytable.PrettyTable(['Kode', 'Waktu', 'Menit'])
        waktuMatkuls = data.getWaktuMatkuls()
        for i in range(0, len(waktuMatkuls)):
            tableWaktuMatkuls.add_row(
                [waktuMatkuls[i].getKode(), waktuMatkuls[i].getWaktu(), str(waktuMatkuls[i].getMenit())])
        print(tableWaktuMatkuls)

    def tampilProdi(self):
        prodis = data.getProdis()
        tabelProdi = prettytable.PrettyTable(['kode', 'nama', 'matkul'])
        for i in range(0, len(prodis)):
            matkuls = prodis.__getitem__(i).getMatkul()
            tempStr = ""
            for j in range(0, len(matkuls)):
                tempStr += matkuls[j].__str__()+"\n "
            tabelProdi.add_row(
                [prodis.__getitem__(i).getNama(), prodis.__getitem__(i).getKode(), tempStr])
        print(tabelProdi)

    def tampilMatkul(self):
        tableMatkuls = prettytable.PrettyTable(
            ['Kode', 'Prodi', 'Nama Matkul', 'Menit', 'Kelas', 'Nama Dosen', 'Jabatan', 'Jenis Ruang', 'Max Peserta'])
        matkuls = data.getMatkuls()
        for i in range(0, len(matkuls)):
            tableMatkuls.add_row(
                [matkuls[i].getKode(), matkuls[i].getProdi(), matkuls[i].getNamaMatkul(), str(matkuls[i].getMenit()), matkuls[i].getKelas(
                ), matkuls[i].getNamaDosen(), matkuls[i].getJabatan(), matkuls[i].getJenis(), str(matkuls[i].getMaxMahasiswa())]
            )
        print(tableMatkuls)

    def tampilGenerasiTeratas(self, populasi):
        tabelGenerasis = prettytable.PrettyTable(
            ['No', 'Fitness', 'Konflik', 'Jadwal'])
        jadwals = populasi.getJadwals()
        for i in range(0, 1):
            hasilJadwal = "-"
            # for j in str(jadwals[i]).split(", "):
            #     hasilJadwal += j+"\n"
            tabelGenerasis.add_row([str(i+1), round(
                jadwals[i].getFitness(), 3), jadwals[i].getKonflik(), hasilJadwal])
        print(tabelGenerasis)

    def tampilGenerasi(self, populasi):
        tabelGenerasis = prettytable.PrettyTable(
            ['No', 'Fitness', 'Konflik', 'Jadwal'])
        jadwals = populasi.getJadwals()
        for i in range(0, len(jadwals)):
            hasilJadwal = "-"
            # for j in str(jadwals[i]).split(", "):
            #     hasilJadwal += j+"\n"
            tabelGenerasis.add_row([str(i+1), round(
                jadwals[i].getFitness(), 3), jadwals[i].getKonflik(), hasilJadwal])
        print(tabelGenerasis)

    def tampilJadwalExcel(self, jadwal):
        jadwal = jadwal.getJadwal()

        jadwalBaru = []
        for i in range(0, len(jadwal)):
            jadwalBaru.append([str(i+1), jadwal[i].getProdi().getNama(),
                               jadwal[i].getMatkul().getNamaMatkul(),
                               jadwal[i].getMatkul().getKelas(),
                               jadwal[i].getMatkul().getMenit(),
                               jadwal[i].getMatkul().getNamaDosen(),
                               jadwal[i].getMatkul().getMaxMahasiswa(),
                               jadwal[i].getMatkul().getJenis(),
                               jadwal[i].getHari().getNama(),
                               jadwal[i].getWaktuMatkul().getWaktu(),
                               jadwal[i].getWaktuMatkul().getMenit(),
                               jadwal[i].getRuangan().getKode(),
                               jadwal[i].getRuangan().getJenis()
                               ])
        df = pd.DataFrame(jadwalBaru, columns=["No.", "Prodi", "Matkul", "Kelas", "Menit", "Dosen",
                                               "Max Mahasiswa", "Jenis Ruang", "Hari", "Waktu", "Menit", "Ruang", "Jenis Ruang"])

        writer = pd.ExcelWriter(
            "jadwal_baru.xlsx", engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Jadwal', index=False)
        worksheet = writer.sheets['Jadwal']
        worksheet.set_column('B:B', 22, None)
        worksheet.set_column('J:J', 14, None)
        writer.save()


data = Data()
tampilData = TampilData()

lenMatkul = len(data.getMatkuls())

UKURAN_POPULASI = int(lenMatkul/2)+lenMatkul
NOMOR_JADWAL_ELIT = 1
UKURAN_PERTANDINGAN_TERPILIH = int(lenMatkul/3)
TINGKAT_MUTASI = 0.1

tampilData.tampilDataTersedia()

noGenerasi = 0
print("\n> Generasi "+str(noGenerasi))
populasi = Populasi(UKURAN_POPULASI)
populasi.getJadwals().sort(key=lambda x: x.getFitness(), reverse=True)
# tampilData.tampilGenerasi(populasi)

algoritmaGenetik = AlgoritmaGenetik()
while(populasi.getJadwals()[0].getFitness() != 1.0):
    noGenerasi += 1
    print("\n> Generasi "+str(noGenerasi))
    populasi = algoritmaGenetik.evolve(populasi)
    populasi.getJadwals().sort(key=lambda x: x.getFitness(), reverse=True)
    tampilData.tampilGenerasiTeratas(populasi)

tampilData.tampilJadwalExcel(populasi.getJadwals()[0])
utils.suaraBeep()
print("\n")
