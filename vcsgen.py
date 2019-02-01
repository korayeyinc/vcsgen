#! /usr/bin/env python3
# -*- coding: utf-8 -*-

'''
File: vcsgen.py
Desc: Command line utility for generating video contact sheets.
Requires: python3-vlc, python3-pil
Version:  0.1
Author:   Koray Eyinç <koray.eyinc@gmail.com>
'''

import argparse
import os
import shutil
import sys
import vlc

from datetime import time
from glob import glob
from pathlib import Path
from time import sleep

from PIL import Image
from PIL import ImageColor
from PIL import ImageDraw
from PIL import ImageFont


class VLC():
    def __init__(self, args):
        self.i = vlc.Instance('--vout=dummy', '--no-audio', '--no-stats', '--quiet', "--no-repeat", "--play-and-exit")
        self.track  = args.input
        self.media  = self.i.media_new(self.track)
        self.player = self.i.media_player_new()
        self.player.set_media(self.media)
        self.width  = args.width
        self.height = args.height
        self.start  = args.start
        self.freq   = args.freq
        self.cols   = args.columns
        self.rows   = args.rows
        self.cells  = args.columns * args.rows
        self.font   = args.font
        self.color  = args.color
        self.header = args.header
        self.logo   = args.logo
        self.tcode  = args.tcode
        self.trname = Path(self.track).stem
        self.snaps  = []


    def run(self):
        '''Runs the player and takes snapshots.'''
        self.player.play()
        # let the player load the VLC modules and other stuff...
        sleep(0.5)
        set_start = False
        c = 0
        while True:
            state = self.player.get_state()
            if (state == vlc.State.Playing):
                if (not set_start):
                    self.forward()
                    set_start = True
                if (c == self.cells):
                    break
                # double time-code workaround
                if (self.snapshot() == True and self.check_snap() == True):
                    c += 1
                    ctime = self.get_ctime()
                    self.timecode(ctime)
                    self.sec_forward()
            elif (state == vlc.State.Ended):
                break
                self.quit_app()


    def check_snap(self):
        try:
            frame = sorted(glob(os.path.join("out", "snaps", "*")))[-1]
            if (os.stat(frame).st_size < 10000):
                os.remove(frame)
                return False
        except IndexError:
            return False
        if (frame in self.snaps):
            return False
        else:
            self.snaps.append(frame)
            return True


    def get_rgb(self, color):
        '''Gets rgb value for given color.'''
        value = ImageColor.getrgb(color)
        return value


    def get_ctime(self):
        '''Gets player current time in time-code format.'''
        pltime  = int(self.player.get_time())
        seconds = int((pltime/1000)%60)
        minutes = int((pltime/(1000*60))%60)
        hours   = int((pltime/(1000*60*60))%24)
        dtime   = time(hours, minutes, seconds)
        ctime   = '{:%H:%M:%S}'.format(dtime)
        return ctime


    def get_dur(self):
        '''Gets media duration in time-code format.'''
        mtime    = int(self.media.get_duration())
        seconds  = int((mtime/1000)%60)
        minutes  = int((mtime/(1000*60))%60)
        hours    = int((mtime/(1000*60*60))%24)
        dtime    = time(hours, minutes, seconds)
        duration = '{:%H:%M:%S}'.format(dtime)
        return duration


    def get_pos(self):
        '''Gets player position.'''
        pos = str(self.player.get_position())
        return pos


    def mspf(self):
        '''Returns milliseconds per frame.'''
        return int(1000 // (self.player.get_fps() or 25))


    def forward(self):
        '''Goes forward till the start time.'''
        start = self.start * 1000
        self.player.set_time(self.player.get_time() + start)


    def sec_forward(self):
        '''Goes forward self.freq seconds.'''
        interval = self.freq * 1000
        self.player.set_time(self.player.get_time() + interval)


    def sec_backward(self):
        '''Goes backward self.freq seconds.'''
        interval = self.freq * 1000
        self.player.set_time(self.player.get_time() - interval)


    def frame_forward(self):
        '''Goes forward one frame.'''
        self.player.set_time(self.player.get_time() + mspf())


    def frame_backward(self):
        '''Goes backward one frame.'''
        self.player.set_time(self.player.get_time() - mspf())


    def media_info(self):
        '''Gets media information.'''
        info = {}
        info["file"]  = "File:    {0}".format(self.trname)
        fbs = os.stat(self.track).st_size
        fgb = round(fbs/(1024*1024*1024), 2)
        dur = self.get_dur()
        info["size"] = "Size:    {0} bytes ({1} GiB), Duration: {2}".format(fbs, fgb, dur)
        audio = self.player.audio_get_track_description()[0][1]
        info["audio"] = "Audio: {0}".format(audio.decode('utf-8'))
        size = self.player.video_get_size(0)
        fps  = round(self.player.get_fps(), 2)
        info["video"] = "Video: {0}x{1}, {2} fps".format(size[0], size[1], fps)
        sub = self.player.video_get_spu()
        info["sub"] = "Subtitles: {0}".format(sub)
        
        return info


    def snapshot(self):
        '''Takes snapshots using the width/height parameters.'''
        out_dir = os.path.join("out", "snaps")
        if (self.player.video_take_snapshot(0, out_dir, self.width, self.height) == 0):
            return True
        else:
            return False


    def timecode(self, tag):
        '''Adds time-code tags to frames'''
        frame = self.snaps[-1]
        img  = Image.open(frame)
        w, h = img.size[0], img.size[1]
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(self.font, self.tcode)
        color = self.color
        draw.text((5, h-20), tag, color, font=font)
        img.save(frame)


    def genvcs(self):
        '''Generates video contact sheet output from snapshot images.'''
        
        frames = sorted(glob(os.path.join("out", "snaps", "*.png")))
        cell = Image.open(frames[0])
        
        header = 100
        w, h = cell.size[0], cell.size[1]
        vcs_size = (w * self.cols, (h * self.rows) + header)
        
        # create a base image for video contact sheet with black background.
        black = self.get_rgb('black')
        img = Image.new('RGBA', vcs_size, black)
        
        # get media info
        info = self.media_info()
        # add header content
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(self.font, self.header)
        text = info['file']
        color = self.color
        draw.text((5, 5),  text, color, font=font)
        text = info['size']
        draw.text((5, 23), text, color, font=font)
        text = info['audio']
        draw.text((5, 41), text, color, font=font)
        text = info['video']
        draw.text((5, 59), text, color, font=font)
        text = info['sub']
        draw.text((5, 77), text, color, font=font)
        
        # add logo image
        logo = Image.open(self.logo)
        lx = vcs_size[0] - (logo.size[0] + 5)
        ly = round((header - logo.size[1]) / 2)
        img.paste(logo, (lx, ly))
        
        # origins for cell frames
        x, y = 0, header
        
        # frame index
        f = 0
        
        for row in range(self.rows):
            for col in range(self.cols):
                frame = Image.open(frames[f])
                img.paste(frame, (x, y))
                x += w
                f += 1
            x = 0
            y += h
        
        filename = self.trname + ".png"
        vcs = os.path.join("out", "vcs", filename)
        
        img.save(vcs)


    def quit_app(self):
        '''Stop and exit'''
        sys.exit(0)


def check_dirs(keep):
    '''Checks if out, vcs and snaps directories exist.'''
    out_dir = "out"
    dst = Path(out_dir)
    
    if (dst.exists() and keep == "no"):
        # clean generated directories and files
        shutil.rmtree(out_dir)
    elif (dst.exists() and keep == "yes"):
        pass
    else:
        dst.mkdir()
    
    snaps_dir = os.path.join("out", "snaps")
    snaps = Path(snaps_dir)
    vcs_dir = os.path.join("out", "vcs")
    vcs = Path(vcs_dir)
    
    if (snaps.exists() and vcs.exists()):
        pass
    else:
        snaps.mkdir()
        vcs.mkdir()


def norm(fpath):
    '''Normalizes file names containing space chars.'''
    fpr = fpath.replace(" ", "_")
    fp = Path(fpath)
    if (fp.exists()):
        fp.rename(fpr)
        fpn = glob(fpr)[0]
    else:
        sys.exit('File not found: ' + fpath)
    
    return fpn


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='PROG', conflict_handler='resolve')
    
    parser.add_argument(
        "-i", "--input",
        type = str,
        default = '',
        help = "Input file to be processed")
    
    parser.add_argument(
        "-w",
        "--width",
        type = int,
        default=512,
        help="Snapshot width")
    
    parser.add_argument(
        "-h",
        "--height",
        type = int,
        default = 0,
        help = "Snapshot height")
    
    parser.add_argument(
        "-s",
        "--start",
        type = int,
        default = 3,
        help = "Snapshot start time")
    
    parser.add_argument(
        "--freq",
        type = int,
        default = 3,
        help = "Snapshot frequency in seconds")
    
    parser.add_argument(
        "--columns",
        type = int,
        default = 2,
        help = "Number of columns for video contact sheet generation")
    
    parser.add_argument(
        "--rows",
        type = int,
        default = 5,
        help = "Number of rows for video contact sheet generation")
    
    font = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
    parser.add_argument(
        "--font",
        type = str,
        default = font,
        help = "TrueType or OpenType font path")
    
    parser.add_argument(
        "--color",
        type = str,
        default = 'white',
        help = "Font color for both caption and time-code. See 'colors.txt' file for full list of color names")
    
    parser.add_argument(
        "--header",
        type = int,
        default = 12,
        help = "Font size for header")
    
    parser.add_argument(
        "--tcode",
        type = int,
        default = 16,
        help = "Font size for time-code")
    
    logo = os.path.join("tests", "data", "logo")
    parser.add_argument(
        "--logo",
        type = str,
        default = logo,
        help = "Logo image path")
    
    parser.add_argument(
        "--keep",
        type = str,
        default = "no",
        help = "Keep files generated previously")
    
    # parse command line arguments
    args = parser.parse_args()
    
    # normalize file names if necessary
    args.input = norm(args.input)
    
    # create directories for snapshots and contact sheets if they don't exist
    check_dirs(args.keep)
    
    # create VLC instantance
    app = VLC(args)
    
    print("[info] Taking snapshots...")
    
    # run the player and take snapshots
    app.run()
    
    print("[info] Generating video contact sheet...")
    
    # generate video contact sheet
    app.genvcs()
    
    print("[info] Done!")

