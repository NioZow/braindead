# Brainless

> Efficiently track YouTube videos and Spotify poadcast so that I can watch stuff without much headache but still have a good tracking.

## Motivation

The motivation for this project is that I like to listen to poadcast and watch YouTube videos to chill out, however, this isn't always productive, and does not help achieving my objectives. That project aims to help me face that problem by solving those :

- Choosing the video : after work, or when eating alone, I just want my brain to chill the *fck* out and so often search YouTube for videos meanwhile. Choosing a video is a real headache, and you can easily get distracted so this project chooses and tracks the videos for you.
- Tracking videos : I don't use a Google account when watching videos, because I truly love the projects that Google creates, buy or maintain, I'm not a big fan of my activity being recorded, and so I don't use a Google Account to limit this. And so this project tracks videos that you watch.
- Notetaking : watching content is great, however, I personally don't remember much of what I watch but don't feel like taking notes, as the main goal is to chill the *fck* out. So I've integrated AI to sum up the videos for me and directly write those to markdown to my notes folder.
- `Taskwarrior` integration : I use `taskwarrior` for task management and this directly interacts with it to make sure I achieve my objectives and track those in my task management workflow.

## Features

- Get all videos and playlists of a youtube channel
- Track the videos and playlists you watch on youtube
- Sum up videos you watch for notetaking and to know if a video is worth watching
- A single command to open a new video to watch in your browser and take notes for it.
- `MongoDB` database (wanted to try it, never used it before)

## Improvements & Ideas

- Scrape my Twitter feed and ask AI the most important to stop scrolling
  - Automatically extract posts (via regex urls) no need for AI.
- Get the most of HackTricks, PayloadAllTheThings little tricks via AI. 
  - Same for channel like LiveOverflow, Nahamsec...
- Notifications when new posts release (feed, todo: implement in THL)
- Harvest CTBB poadcast description links. Those contain useful resources.
