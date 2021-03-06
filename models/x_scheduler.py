# -*- coding: utf-8 -*-

import os
import time
import subprocess
from gluon.contrib.simplejson import loads, dumps
import urllib

from pytube import YouTube

from ednet.ad import AD
from ednet import Faculty
from ednet import Student

# Task Scheduler Code


def update_media_meta_data(media_file):
    print "Found Json: ", media_file
    
    # Open the json file
    try:
        f = open(media_file, "r")
        tmp = f.read()
        meta = loads(tmp)
        f.close()
        
        # See if the item is in the database
        item = db.media_files(media_guid=meta['media_guid'])
        if item is None:
            # Record not found!
            print "Record not found: ", meta['media_guid']
            db.media_files.insert(media_guid=meta['media_guid'], title=meta['title'], description=meta['description'], category=meta['category'],
                               tags=loads(meta['tags']), width=meta['width'], height=meta['height'], quality=meta['quality'], media_type=meta['media_type'])
            db.commit()
        else:
            print "Record FOUND: ", meta['media_guid']
            item.update_record(title=meta['title'], description=meta['description'], category=meta['category'],
                               tags=loads(meta['tags']), width=meta['width'], height=meta['height'], quality=meta['quality'], media_type=meta['media_type'])
            db.commit()
    except Exception as ex:
        print "Error processing media file: ", media_file, str(ex)
        db.rollback()
    
    

def update_media_database_from_json_files():
    # Go through the media files and find json files that aren't
    # already in the database.
    # This is useful for when we copy movie files back and forth between systems
    #Starts in the Models folder
    w2py_folder = os.path.abspath(__file__)
    #print "Running File: " + app_folder
    w2py_folder = os.path.dirname(w2py_folder)
    # app folder
    w2py_folder = os.path.dirname(w2py_folder)
    app_folder = w2py_folder
    # Applications folder
    w2py_folder = os.path.dirname(w2py_folder)
    # Root folder
    w2py_folder = os.path.dirname(w2py_folder)
    #print "W2Py Folder: " + w2py_folder
    target_folder = os.path.join(app_folder, 'static')
    
    # base folder for media files
    target_folder = os.path.join(target_folder, 'media')
    
    # Walk the folders/files
    print "looking in: " + target_folder
    for root, dirs, files in os.walk(target_folder):
        for f in files:
            if f.endswith("json"):
                f_path = os.path.join(root, f)
                update_media_meta_data(f_path)
    pass
    return True


def process_media_file(media_id):
    ret = ""
    
    # Find ffmpeg binary
    ffmpeg = "/usr/bin/ffmpeg"
    if (os.path.isfile(ffmpeg) != True):
        ffmpeg = "/usr/local/bin/ffmpeg "
    if (os.path.isfile(ffmpeg) != True):
        ret = "ERROR - NO FFMPEG APP FOUND! " + ffmpeg
        print ret
        return ret
    
    # Grab the media file
    #media_file = None
    media_file = db(db.media_file_import_queue.id==media_id).select().first()
    if (media_file == None):
        return dict(error="Invalid Media File")
    else:
        print "Processing media file: " + str(media_id) + " [" + str(time.time()) + "]"
        
    db(db.media_file_import_queue.id==media_id).update(status='processing')
    # Make sure to do this and unlock the db
    db.commit()
    
    #Starts in the Models folder
    w2py_folder = os.path.abspath(__file__)
    #print "Running File: " + app_folder
    w2py_folder = os.path.dirname(w2py_folder)
    # app folder
    w2py_folder = os.path.dirname(w2py_folder)
    app_folder = w2py_folder
    # Applications folder
    w2py_folder = os.path.dirname(w2py_folder)
    # Root folder
    w2py_folder = os.path.dirname(w2py_folder)
    #print "W2Py Folder: " + w2py_folder
    
    # Get the uploads path (something like /var/www/clients/client1/web1/web/applications/smc/uploads/media_files.media_file/b6)
    tmp_path = db.media_file_import_queue.media_file.retrieve_file_properties(db.media_file_import_queue(media_file.id).media_file)['path']
    #NOTE Has stupid databases/../uploads in the path, replace databases/../ with nothing
    tmp_path = tmp_path.replace('databases/../', '')
    #print "TmpPath: " + tmp_path
    
    uploads_folder = os.path.join(w2py_folder, tmp_path)
    #print "Upload Path: " + uploads_folder
    input_file = os.path.join(uploads_folder, media_file.media_file)
    
    #print "Processing media file: " + input_file + " [" + str(time.time()) + "]"
    
    # Figure out output file name (use media guid)
    # static/media/01/010102alj29vsor3.webm
    file_guid = media_file.media_guid.replace('-', '')
    #print "File GUID: " + str(file_guid)
    target_folder = os.path.join(app_folder, 'static')
    
    target_folder = os.path.join(target_folder, 'media')
        
    file_prefix = file_guid[0:2]
    
    target_folder = os.path.join(target_folder, file_prefix)
    #print "Target Dir: " + target_folder
    
    try:
        os.makedirs(target_folder)
    except OSError, message:
        pass
    
    target_file = os.path.join(target_folder, file_guid)
    
    output_webm =  target_file + ".webm"
    output_ogv = target_file + ".ogv"
    output_mp4 = target_file + ".mp4"
    output_mobile_mp4 = target_file + ".mobile.mp4"
    output_meta = target_file + ".json"
    output_poster = target_file + ".poster.png"
    output_thumb = target_file + ".thumb.png"
    
    print "Output files: "
    print output_webm
    print output_ogv
    print output_mp4
    
    webm_ret = ""
    ogv_ret = ""
    mp4_ret = ""
    poster_ret = ""
    thumb_ret = ""
    
    # Run ffmpeg to process file
    
    # Do webm - NOTE No webm support in ffmpeg right now - # TODO unknown encoder libvpx
    #cmd = ffmpeg + " -i '" + input_file + "' -vcodec libvpx -qscale 6 -acodec libvorbis -ab 128k -vf scale='480:-1' '" + output_webm + "'"
    #p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    #webm_ret = p.communicate()[0]
    
    # Do OGV
    #cmd = ffmpeg + " -y -i '" + input_file + "' -vcodec libtheora -qscale 6 -acodec libvorbis -ab 192k -vf scale='640:-1' '" + output_ogv + "'"
    cmd = ffmpeg + " -y -i '" + input_file + "' -vcodec libtheora -qscale:v 5 -acodec libvorbis -ab 128k '" + output_ogv + "'"
    #print "Creating OGV..."  + " [" + str(time.time()) + "]"
    print "!clear!10%"
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    ogv_ret = p.communicate()[0]
    
    
    # Do MP4
    #cmd = ffmpeg + " -y -i '" + input_file + "' -vcodec libx264 -preset slow -profile main -crf 20 -acodec libfaac -ab 192k -vf scale='720:-1' '" + output_mp4 + "'"
    cmd = ffmpeg + " -y -i '" + input_file + "' -vcodec libx264 -preset slow -movflags faststart -profile:v main -crf 20 -acodec aac -ab 128k '" + output_mp4 + "'"
    #print "Creating MP4..."  + " [" + str(time.time()) + "]"
    print "!clear!30%"
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    mp4_ret = p.communicate()[0]
    
    # Do MP4 with mobile quality
    cmd = ffmpeg + " -y -i '" + input_file + "' -vcodec libx264 -preset slow -movflags faststart -profile main -crf 20 -acodec aac -ab 128k -vf scale='2*trunc(oh*a/2):480' '" + output_mobile_mp4 + "'"
    #print "Creating mobile MP4..."  + " [" + str(time.time()) + "]"
    print "!clear!70%"
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    mp4_ret += p.communicate()[0]
    
    
    # Generate poster image
    cmd = ffmpeg + " -y -ss 5 -i '" + input_file + "' -vf  'thumbnail,scale=640:-1' -frames:v 1 '" + output_poster + "'"
    #print "Creating poster image..." + " [" + str(time.time()) + "]"
    print "!clear!85%"
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    poster_ret = p.communicate()[0]
    
    # Generate thumbnail image
    cmd = ffmpeg + " -y -ss 5 -i '" + input_file + "' -vf  'thumbnail,scale=128:-1' -frames:v 1 '" + output_thumb + "'"
    #print "Creating thumbnail image..."  + " [" + str(time.time()) + "]"
    print "!clear!95%"
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    thumb_ret = p.communicate()[0]
    
    
    # -vf scale="480:2*trunc(ow*a/2)"
    # ffmpeg -i [your video] [encoding options as specified above] [your output video with appropriate extension - eg output.mp4, output.ogv or output.webm]
    
    # Make webm file - 480p
    #cmd = ffmpeg + " -i 'input_file.avi' -codec:v libvpx -quality good -cpu-used 0 -movflags faststart -b:v 600k -maxrate 600k -bufsize 1200k -qmin 10 -qmax 42 -vf scale=-1:480 -threads 4 -codec:a vorbis -b:a 128k output_file.webm"
    # -vcodec libvpx -qscale 6 -acodec libvorbis -ab 128k
    
    
    # Make ogv file
    #cmd = ""
    # -vcodec libtheora -qscale 6 -acodec libvorbis -ab 128k
    
    # Make mp4 file - 480p
    #cmd = ffmpeg + " -i inputfile.avi -codec:v libx264 -profile:v main -preset slow -movflags faststart -b:v 400k -maxrate 400k -bufsize 800k -vf scale=-1:480 -threads 0 -codec:a libfdk_aac -b:a 128k output.mp4"  #codec:a libfdk_aac  codec:a mp3
    #-vcodec libx264 -preset slow -profile main -crf 20 -acodec libfaac -ab 128k
    
    
    # Update file info
    
    db.media_files.insert(title=media_file.title,
                          media_guid=media_file.media_guid.replace('-', ''),
                          description=media_file.description,
                          original_file_name=media_file.original_file_name,
                          media_type=media_file.media_type,
                          category=media_file.category,
                          tags=media_file.tags,
                          width=media_file.width,
                          height=media_file.height,
                          quality=media_file.quality
                          )
    
    #media_file.update(status='done')
    db(db.media_file_import_queue.id==media_id).delete()
    
    # Have to call commit in tasks if changes made to the db
    db.commit()
    
    # Dump meta data to the folder along side the video files
    # This can be used for export/import
    meta = {'title': media_file.title, 'media_guid':media_file.media_guid.replace('-', ''),
            'description':media_file.description,'original_file_name':media_file.original_file_name,
            'media_type':media_file.media_type, 'category':media_file.category,
            'tags': dumps(media_file.tags), 'width':media_file.width,
            'height':media_file.height, 'quality':media_file.quality}
    
    meta_json = dumps(meta)
    f = os.open(output_meta, os.O_TRUNC|os.O_WRONLY|os.O_CREAT)
    os.write(f, meta_json)
    os.close(f)
    
    print "!clear!100%"
    
    return dict(mp4_ret=mp4_ret,ogv_ret=ogv_ret,webm_ret=webm_ret, poster_ret=poster_ret, thumb_ret=thumb_ret)

def remove_old_wamap_video_files():
    # Loop through the old table and remove the video files
    rows = db(db.wamap_questionset).select()
    db.commit()
    
    # Make sure we are in the correct current directory
    #Starts in the Models folder
    w2py_folder = os.path.abspath(__file__)
    #print "Running File: " + app_folder
    w2py_folder = os.path.dirname(w2py_folder)
    # app folder
    w2py_folder = os.path.dirname(w2py_folder)
    app_folder = w2py_folder
    # Applications folder
    w2py_folder = os.path.dirname(w2py_folder)
    # Root folder
    w2py_folder = os.path.dirname(w2py_folder)
    #print "W2Py Folder: " + w2py_folder
    
    # Ensure the wamap folder exists
    wamap_folder = os.path.join(app_folder, "static")
    wamap_folder = os.path.join(wamap_folder, "media")
    wamap_folder = os.path.join(wamap_folder, "wamap")
    
    if (os.path.isdir(wamap_folder) != True):
        os.mkdir(wamap_folder)
    
    removed = []
    not_removed = []
    for row in rows:
        # Remove the file if it exists
        fpath = os.path.join(wamap_folder, "wamap_" + str(row.wamap_id) + ".mp4")
        if (os.path.exists(fpath) == True):
            try:
                print "removing " + fpath  + " [" + str(time.time()) + "]"
                os.remove(fpath)
                removed.append(fpath)
            except:
                print "error removing " + fpath  + " [" + str(time.time()) + "]"
                not_removed.append(fpath)
        else:
            print "skipping " + fpath  + " [" + str(time.time()) + "]"
            not_removed.append(fpath)
    print "Done." + str(time.time())
    #return dict(removed=removed, not_removed=not_removed)
    return True

def process_wamap_video_links():
    # Make sure we are in the correct current directory
    #Starts in the Models folder
    w2py_folder = os.path.abspath(__file__)
    #print "Running File: " + app_folder
    w2py_folder = os.path.dirname(w2py_folder)
    # app folder
    w2py_folder = os.path.dirname(w2py_folder)
    app_folder = w2py_folder
    # Applications folder
    w2py_folder = os.path.dirname(w2py_folder)
    # Root folder
    w2py_folder = os.path.dirname(w2py_folder)
    #print "W2Py Folder: " + w2py_folder
    
    # Ensure the wamap folder exists
    wamap_folder = os.path.join(app_folder, "static")
    wamap_folder = os.path.join(wamap_folder, "media")
    wamap_folder = os.path.join(wamap_folder, "wamap")
    
    if (os.path.isdir(wamap_folder) != True):
        os.mkdir(wamap_folder)
    
    process_count = 50
    last_row = 0
    
    while (process_count > 0):
        process_count -= 1
        
        
        had_errors = False
        item = db(db.wamap_videos.downloaded==False).select().first()
        db.commit()
        ret = ""
        if (item == None):
            ret += "Out of wamap items to process"
            print "Done processing videos."
            return dict(ret=ret)
        
        print "-----------------------\n"
        print "Processing " + str(item.source_url) + "\n"
        last_row = item.id
        
        yt_url = item.source_url
        if (('youtube.com' in yt_url or 'youtu.be' in yt_url) and "admin.correctionsed.com" not in yt_url):
            # check if the file already exists
            vidfile = os.path.join(wamap_folder, "wamap_" + str(item.media_guid))
            #print "Checking vid file: " + vidfile + ".mp4"
            if (os.path.exists(vidfile + ".mp4") != True):
                #print "Downloading video: " + str(yt_url)
                # download the video
                try:
                    os.chdir(wamap_folder)
                    # Store the original link in a link file
                    meta = {'media_guid':item.media_guid, 'yt_url':yt_url}
                    meta_json = dumps(meta)
                    f = os.open("wamap_" + str(item.media_guid) + ".link", os.O_TRUNC|os.O_WRONLY|os.O_CREAT)
                    os.write(f, meta_json)
                    os.close(f)
                    
                    # Download the video from the internet
                    yt = YouTube()
                    yt_url = yt_url.replace("!!1", "").replace("!!0", "") #because some urls end up with the 
                    # field seperator still in it
                    if ("/embed/" in yt_url):
                        # Embedded link doesn't return correctly, change it back
                        # to normal link
                        yt_url = yt_url.replace("/embed/", "/watch?v=")
                    yt.url = yt_url
                    yt.filename = "wamap_" + str(item.media_guid)
                    f = yt.filter('mp4')[-1]
                    f.download()                    
                except Exception, e:
                    print " ****** Error fetching movie ****** " + str(e)
                    had_errors = True
                os.chdir(w2py_folder)
            else:
                pass
                #print "Video already downloaded " + str(vidfile)
            
            #update wamap db??
            if (had_errors != True):
                if (os.path.exists(vidfile + ".mp4") == True):
                    new_url = "https://admin.correctionsed.com/media/wmplay/" + str(item.media_guid)
                    #print " Updating (" + str(yt_url) + ") to point to (" + new_url + ")"
                    db(db.wamap_videos.id==item.id).update(new_url=new_url)
                    db.commit()
                    
                    db_wamap = DAL('mysql://smc:aaaaaaa!!@wamap.correctionsed.com/imathsdb')
                    
                    # Update all locations...
                    #DEBUG TODO - 
                    #imas_inlinetext (text column)
                    sql = "UPDATE imas_inlinetext SET `text`=REPLACE(`text`, '" + yt_url + "', '" + new_url + "') WHERE `text` like '%" + yt_url + "%'"
                    #print sql
                    db_wamap.executesql(sql)
                    
                    #imas_assessments (intro colum  youtube embed link?)
                    sql = "UPDATE imas_assessments SET `intro`=REPLACE(`intro`, '" + yt_url + "', '" + new_url + "') WHERE `intro` like '%" + yt_url + "%'"
                    #print sql
                    db_wamap.executesql(sql)
                    
                    #imas_linkedtext (summary column)
                    sql = "UPDATE imas_linkedtext SET `summary`=REPLACE(`summary`, '" + yt_url + "', '" + new_url + "') WHERE `summary` like '%" + yt_url + "%'"
                    #print sql
                    db_wamap.executesql(sql)
                    
                    #imas_linkedtext (text column)
                    sql = "UPDATE imas_linkedtext SET `text`=REPLACE(`text`, '" + yt_url + "', '" + new_url + "') WHERE `text` like '%" + yt_url + "%'"
                    #print sql
                    db_wamap.executesql(sql)
                    
                    #imas_questionset (control)
                    sql = "UPDATE imas_questionset SET `control`=REPLACE(`control`, '" + yt_url + "', '" + new_url + "') WHERE `control` like '%" + yt_url + "%'"
                    #print sql
                    db_wamap.executesql(sql)
                    
                    #imas_questionset (qtext)
                    sql = "UPDATE imas_questionset SET `qtext`=REPLACE(`qtext`, '" + yt_url + "', '" + new_url + "') WHERE `qtext` like '%" + yt_url + "%'"
                    #print sql
                    db_wamap.executesql(sql)
                    
                    #imas_questionset (extref)
                    sql = "UPDATE imas_questionset SET `extref`=REPLACE(`extref`, '" + yt_url + "', '" + new_url + "') WHERE `extref` like '%" + yt_url + "%'"
                    #print sql
                    db_wamap.executesql(sql)
                    
                    db_wamap.commit()
                    db_wamap.close()
        else:
            print "No youtube link found (" + str(item.source_url) + ")"
        
        db(db.wamap_videos.id==item.id).update(downloaded=True)
        db.commit()
    
    return dict(ret=ret, last_row=last_row)


def create_home_directory(user_name, home_directory):
    print "Creating home directory for: " + user_name  + " [" + str(time.time()) + "]"
    ret = AD.CreateHomeDirectory(user_name, home_directory)
    print "Done Creating home directory for: " + user_name  + " [" + str(time.time()) + "]"
    print "Result: " + ret
    return ret

def download_wamap_qimages():
    ret = True
    # Make sure we are in the correct current directory
    #Starts in the Models folder
    w2py_folder = os.path.abspath(__file__)
    #print "Running File: " + app_folder
    w2py_folder = os.path.dirname(w2py_folder)
    # app folder
    w2py_folder = os.path.dirname(w2py_folder)
    app_folder = w2py_folder
    # Applications folder
    w2py_folder = os.path.dirname(w2py_folder)
    # Root folder
    w2py_folder = os.path.dirname(w2py_folder)
    #print "W2Py Folder: " + w2py_folder
    
    # -------- Process qimages files --------
    # Download them
    
    # Ensure the wamap folder exists
    wamap_folder = os.path.join(app_folder, "static")
    wamap_folder = os.path.join(wamap_folder, "media")
    wamap_folder = os.path.join(wamap_folder, "wamap")
    pdfs_folder = os.path.join(wamap_folder, "pdfs")
    wamap_folder = os.path.join(wamap_folder, "qimages")
    
    if (os.path.isdir(wamap_folder) != True):
        os.mkdir(wamap_folder)
    if (os.path.isdir(pdfs_folder) != True):
        os.mkdir(pdfs_folder)
    
    
    # Loop over each distinct qimages entry
    rs = db(db.wamap_qimages).select(db.wamap_qimages.source_filename, distinct=True)
    for row in rs:
        source_url = "https://www.wamap.org/assessment/qimages/" + row["source_filename"]
        s3_source_url = "https://s3.amazonaws.com/wamapdata/qimages/" + row["source_filename"]
        local_path = os.path.join(wamap_folder, row["source_filename"])
        if (os.path.exists(local_path) == True):
            if '<title>404' in open(local_path).read():
                pass # File has 404 error, try again
            else:
                continue # Skip trying to download if the file is already there
        try:
            print "Downloading " + row["source_filename"]
            urllib.urlretrieve(source_url, local_path)
            if '<title>404' in open(local_path).read():
                # Didn't find, try dl from amazonaws
                urllib.urlretrieve(s3_source_url, local_path)
        except Exception, e:
            print "Exception trying to download " + source_url + "(" + str(e) + ")"
            ret = False
    
    # -------- Process imas_instr_files -------- 
    # Just download them
    
    # Ensure the wamap folder exists
    wamap_folder = os.path.join(app_folder, "static")
    wamap_folder = os.path.join(wamap_folder, "media")
    wamap_folder = os.path.join(wamap_folder, "wamap")
    wamap_folder = os.path.join(wamap_folder, "inst_files")
    
    if (os.path.isdir(wamap_folder) != True):
        os.mkdir(wamap_folder)
    
    db_wamap = DAL('mysql://smc:aaaaaaa!!@wamap.correctionsed.com/imathsdb')
    # Loop over each distinct instr_files entry
    rs = db_wamap.executesql("select filename from `imas_instr_files`")
    for row in rs:
        source_url = "https://www.wamap.org/course/files/" + row[0]
        alt_source_url = "https://s3.amazonaws.com/wamapdata/cfiles/" + row[0]
        local_path = os.path.join(wamap_folder, row[0])
        if (os.path.exists(local_path) == True):
            if '<title>404' in open(local_path).read():
                pass # File has 404 error, try again
            else:
                continue # Skip trying to download if the file is already there
        try:
            print "Downloading " + row[0]
            urllib.urlretrieve(source_url, local_path)
            if '<title>404' in open(local_path).read():
                # Didn't find, try dl from amazonaws
                #print "404 getting " + source_url
                urllib.urlretrieve(alt_source_url, local_path)
        except Exception, e:
            print "Exception trying to download " + source_url + "(" + str(e) + ")"
            ret = False
    
    
    # -------- Process imas_linkedtext -------- 
    # Download what we can and adjust the links
    # Only grab PDF files for now
    # Loop over each distinct pdf entry
    rs = db(db.wamap_pdfs).select()
    for row in rs:
        source_url = row.source_url
        local_path = os.path.join(pdfs_folder, row.media_guid + ".pdf")
        if (os.path.exists(local_path) == True):
            if '<title>404' in open(local_path).read():
                pass # File has 404 error, try again
            else:
                new_url = "https://admin.correctionsed.com/static/media/wamap/pdfs/" + str(row.media_guid) + ".pdf"
                print " Updating (" + str(source_url) + ") to point to (" + new_url + ")"
                db(db.wamap_pdfs.id==row.id).update(new_url=new_url)
                db.commit()
                continue # Skip trying to download if the file is already there
        try:
            print "Downloading " + row.source_url
            urllib.urlretrieve(source_url, local_path)
            if '<title>404' in open(local_path).read():
                print "404 getting " + source_url
                # Didn't find, try dl from amazonaws
                #urllib.urlretrieve(s3_source_url, local_path)
            else:
                os.chdir(pdfs_folder)
                # Store the original link in a link file
                meta = {'media_guid':row.media_guid, 'source_url':source_url}
                meta_json = dumps(meta)
                f = os.open("wamap_" + str(row.media_guid) + ".link", os.O_TRUNC|os.O_WRONLY|os.O_CREAT)
                os.write(f, meta_json)
                os.close(f)
                new_url = "https://admin.correctionsed.com/static/media/wamap/pdfs/" + str(row.media_guid) + ".pdf"
                print " Updating (" + str(source_url) + ") to point to (" + new_url + ")"
                db(db.wamap_pdfs.id==row.id).update(new_url=new_url)
                db.commit()
        except Exception, e:
            print "Exception trying to download " + source_url + "(" + str(e) + ")"
            ret = False
    
    # Update PDF links!!
    rs = db(db.wamap_pdfs).select()
    for row in rs:
        # Replace this url with the new one
        old_url = row.source_url
        new_url = row.new_url
        if (new_url == ""):
            continue # Skip empty urls
        # Pull pdfs from imas_questionset.extref
        t = "imas_questionset"
        c = "extref"
        sql = "UPDATE " + t + " SET `" + c + "`=REPLACE(`" + c + "`, '" + old_url + "', '" + new_url + "') WHERE `" + c + "` like '%" + old_url + "%'"
        print "SQL: " + sql
        db_wamap.executesql(sql)
        
        # Pull pdfs from imas_questionset.control
        t = "imas_questionset"
        c = "control"
        sql = "UPDATE " + t + " SET `" + c + "`=REPLACE(`" + c + "`, '" + old_url + "', '" + new_url + "') WHERE `" + c + "` like '%" + old_url + "%'"
        print "SQL: " + sql
        db_wamap.executesql(sql)
        
        # Pull pdfs from imas_questionset.qtext
        t = "imas_questionset"
        c = "qtext"
        sql = "UPDATE " + t + " SET `" + c + "`=REPLACE(`" + c + "`, '" + old_url + "', '" + new_url + "') WHERE `" + c + "` like '%" + old_url + "%'"
        print "SQL: " + sql
        db_wamap.executesql(sql)
        
        # Pull pdfs from imas_inlinetext.text
        t = "imas_inlinetext"
        c = "text"
        sql = "UPDATE " + t + " SET `" + c + "`=REPLACE(`" + c + "`, '" + old_url + "', '" + new_url + "') WHERE `" + c + "` like '%" + old_url + "%'"
        print "SQL: " + sql
        db_wamap.executesql(sql)
        
        # Pull pdfs from imas_assessments.intro
        t = "imas_assessments"
        c = "intro"
        sql = "UPDATE " + t + " SET `" + c + "`=REPLACE(`" + c + "`, '" + old_url + "', '" + new_url + "') WHERE `" + c + "` like '%" + old_url + "%'"
        print "SQL: " + sql
        db_wamap.executesql(sql)
        
        # Pull pdfs from imas_linkedtext.summary
        t = "imas_linkedtext"
        c = "summary"
        sql = "UPDATE " + t + " SET `" + c + "`=REPLACE(`" + c + "`, '" + old_url + "', '" + new_url + "') WHERE `" + c + "` like '%" + old_url + "%'"
        print "SQL: " + sql
        db_wamap.executesql(sql)
        
        # Pull pdfs from imas_linkedtext.text
        t = "imas_linkedtext"
        c = "text"
        sql = "UPDATE " + t + " SET `" + c + "`=REPLACE(`" + c + "`, '" + old_url + "', '" + new_url + "') WHERE `" + c + "` like '%" + old_url + "%'"
        print "SQL: " + sql
        db_wamap.executesql(sql)
        db_wamap.commit()
        
    db_wamap.close()
    return ret


def refresh_all_ad_logins():
    # Go to the AD server and refresh all student and staff AD login times
    ret = ""
    
    # Update the last login value for all users (students and faculty)
    if (AD.ConnectAD() != True):
        ret = "[AD Disabled]"
        return ret
    
    # Grab list of students
    rows = db(db.student_info).select(db.student_info.user_id)
    for row in rows:
        #ret += "UID: " + row.user_id
        ll = Student.GetLastADLoginTime(row.user_id)
        #if (ll == None):
        #    ret += "None"
        #else:
        #    ret += str(ll)
        db(db.student_info.user_id==row.user_id).update(ad_last_login=ll)
        pass
        db.commit()
    
    # Grab a list of faculty
    rows = db(db.faculty_info).select(db.faculty_info.user_id)
    for row in rows:
        #ret += "UID: " + row.user_id
        ll = Faculty.GetLastADLoginTime(row.user_id)
        #if (ll == None):
        #    ret += "None"
        #else:
        #    ret += str(ll)
        db(db.faculty_info.user_id==row.user_id).update(ad_last_login=ll)
        pass
        db.commit()
    
    rows=None
    ad_errors = AD.GetErrorString()
    ret = "Done."
    
    return ret

# Enable the scheduler
from gluon.scheduler import Scheduler

scheduler = Scheduler(db_scheduler, max_empty_runs=100, heartbeat=1,
                      group_names=['process_videos', 'create_home_directory', 'wamap_delete', 'wamap_videos', 'misc'],
                      tasks=dict(process_media_file=process_media_file,
                                 process_wamap_video_links=process_wamap_video_links,
                                 create_home_directory=create_home_directory,
                                 remove_old_wamap_video_files=remove_old_wamap_video_files,
                                 download_wamap_qimages=download_wamap_qimages,
                                 refresh_all_ad_logins=refresh_all_ad_logins,
                                 update_media_database_from_json_files=update_media_database_from_json_files,
                                 ))
current.scheduler = scheduler


# Make sure to run the ad login refresh every hour or so
refresh_ad_login = current.cache.ram('refresh_ad_login', lambda: True, time_expire=60*60)
if refresh_ad_login is True:
    current.cache.ram('refresh_ad_login', lambda: False, time_expire=0)
    # Update the last login value for all users (students and faculty)
    if (AD.ConnectAD() != True):
        # Not enabled, skip
        pass
    else:
        # Schedule the process
        result = scheduler.queue_task('refresh_all_ad_logins', timeout=1200, immediate=True, sync_output=5, group_name="misc", repeats=1, period=0)
        pass
    
    # Make sure to start the scheduler process
    cmd = "/usr/bin/nohup /usr/bin/python " + os.path.join(request.folder, 'static/scheduler/start_misc_scheduler.py') + " > /dev/null 2>&1 &"
    p = subprocess.Popen(cmd, shell=True, close_fds=True)
