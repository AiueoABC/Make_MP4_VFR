videoFilename = './video.mp4'
outputFilename = './testVFR.mp4'
timecodesFilename = './timecodes.txt'

with open(videoFilename, 'rb') as f:
    data = f.read()

with open(timecodesFilename) as f1:
    times_str = f1.read().splitlines()
    times = [int(float(s)) for s in times_str]

index_mdat = data.find(b'mdat')
index_moov = data.find(b'moov')  # データサイズ代わるので
index_trak = data.find(b'trak')  # データサイズ代わるので1
index_mdia = data.find(b'mdia')  # データサイズ代わるので2
index_minf = data.find(b'minf')  # データサイズ代わるので3
index_stbl = data.find(b'stbl')  # データサイズ代わるので4
index_stts = data.find(b'stts')  # データサイズ代わるので5
index_stss = data.find(b'stss')

if index_mdat >= 0 and index_stts >= 0 and index_stss >= 0:
    if index_stts - index_mdat > 0:  # mdatが先にないとstcoを書き換える必要が出てめんどくさい
        data1 = b''  # data1とdata2でサンドイッチする
        data2 = b''
        if index_stss - index_stts == 24:  # 24 - 8 = 16 この時はMovieがCFRになっているはず
            total_frames = int(data[index_stts + 12:index_stts + 16].hex(), 16)
            # total_frames = data[index_stts + 12] * 256 ** 3 + data[index_stts + 13] * 256 ** 2 + \
            #                data[index_stts + 14] * 256 + data[index_stts + 15]
            data1 = data[:index_stts - 4]
            datasizeSTTS = total_frames * 8 + 8
            datasizedifferenceSTTS = datasizeSTTS - int(data[index_stts - 4:index_stts].hex(), 16)
            data2_0 = bytes.fromhex(hex(datasizeSTTS)[2:].zfill(8))  # stts data size
            # stts data size = 8(total_frame + 1(data frames num) - 1(timedelta num))+8
            data2 = data[index_stts:index_stts+8]  # stts0000"73 74 74 73 00 00 00 00"
            data3 = data[index_stss:]  # stssからさきっぽまで
            data_initiator = bytes.fromhex(hex(total_frames - 1)[2:].zfill(8))  # データ総数を書くらしい、タイムスタンプだと差分だから -1　する
            frame_data_initiator = b'\x00\x00\x00\x01'  # タイムスタンプの前につくみたい
            data_terminator = b'\x00\x00\x00\x30'  # 最後のデータの後ろにつくみたい (右端は次のブロックのデータ数）

            data2sandwich = data_initiator
            old_timestamp = times[0]
            for timestamp in times[1:]:
                time_delta = timestamp - old_timestamp
                time_data = bytes.fromhex(hex(time_delta)[2:].zfill(8))
                old_timestamp = timestamp
                data2sandwich = data2sandwich + frame_data_initiator + time_data
            data2sandwich = data2sandwich + data_terminator
            new_data = data1 + data2_0 + data2 + data2sandwich + data3

            # 各ブロックのデータサイズを書き換える
            index_moov = new_data.find(b'moov')  # データサイズ代わるので
            new_data = new_data[:index_moov - 4] + bytes.fromhex(hex(datasizedifferenceSTTS + int(new_data[index_moov - 4:index_moov].hex(), 16))[2:].zfill(8)) + new_data[index_moov:]
            index_trak = new_data.find(b'trak')  # データサイズ代わるので1
            new_data = new_data[:index_trak - 4] + bytes.fromhex(hex(datasizedifferenceSTTS + int(new_data[index_trak - 4:index_trak].hex(), 16))[2:].zfill(8)) + new_data[index_trak:]
            index_mdia = new_data.find(b'mdia')  # データサイズ代わるので2
            new_data = new_data[:index_mdia - 4] + bytes.fromhex(hex(datasizedifferenceSTTS + int(new_data[index_mdia - 4:index_mdia].hex(), 16))[2:].zfill(8)) + new_data[index_mdia:]
            index_minf = new_data.find(b'minf')  # データサイズ代わるので3
            new_data = new_data[:index_minf - 4] + bytes.fromhex(hex(datasizedifferenceSTTS + int(new_data[index_minf - 4:index_minf].hex(), 16))[2:].zfill(8)) + new_data[index_minf:]
            index_stbl = new_data.find(b'stbl')  # データサイズ代わるので4
            new_data = new_data[:index_stbl - 4] + bytes.fromhex(hex(datasizedifferenceSTTS + int(new_data[index_stbl - 4:index_stbl].hex(), 16))[2:].zfill(8)) + new_data[index_stbl:]

            #再生時間を書き換える
            index_tkhd = data.find(b'tkhd')
            original_duration = int(data[index_tkhd+4+16:index_tkhd+4+24].hex(), 16)
            new_duration = times[-1] + 1
            new_data = new_data[:index_tkhd+4+16] + bytes.fromhex(hex(new_duration)[2:].zfill(16)) + new_data[index_tkhd+4+24:]

            index_mvhd = data.find(b'mvhd')
            timescale = int(data[index_mvhd+4+12:index_mvhd+4+16].hex(), 16)
            new_data = new_data[:index_mvhd+4+16] + bytes.fromhex(hex(new_duration)[2:].zfill(8)) + new_data[index_mvhd+4+20:]

            index_mdhd = data.find(b'mdhd')
            new_data = new_data[:index_mdhd+4+16] + bytes.fromhex(hex(new_duration)[2:].zfill(8)) + new_data[index_mdhd+4+20:]
            new_data = new_data[:index_mdhd+4+12] + bytes.fromhex(hex(timescale)[2:].zfill(8)) + new_data[index_mdhd+4+16:]

            with open(outputFilename, 'wb') as f2:
                f2.write(new_data)

else:
    print('Something is wrong with MP4 file... (FileBroken)')
