import os
import time
import audio_helper
from youtube_to_audio import process_audio
from elevenlabs import clone, generate, play, save
import logging

log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.basicConfig(level=getattr(logging, log_level),
                    format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger()

def main(video_urls, voice_name, filename, description=""):
    # Start timing
    start_time = time.time()

    voice_files = []
    for index, video_url in enumerate(video_urls):
        logger.info(f"Processing video {index + 1}/{len(video_urls)}...")
        processing_start_time = time.time()
        folder_name = f"audio_clips/{voice_name}_{index}_{processing_start_time}"
        process_audio(video_url, folder_name, filename)

        # Add the voice files from this folder to the list
        voice_files.extend([
            os.path.join(folder_name, f) 
            for f in os.listdir(folder_name) 
            if f.startswith(filename) and "_part" in f
        ])
        logger.info(f"Finished video {index + 1}/{len(video_urls)}. Time taken: {time.time() - processing_start_time} seconds")

    # Total files before filtering
    total_files_before = len(voice_files)
    total_size_before = sum(os.path.getsize(f) for f in voice_files)

    # Sort voice files by size, filter out any greater than 10MB, and take the top 25
    voice_files = sorted(voice_files, key=os.path.getsize, reverse=True)
    voice_files = [f for f in voice_files if os.path.getsize(f) <= 10 * 1024 * 1024][:25]

    # Total files after filtering
    total_files_after = len(voice_files)
    total_size_after = sum(os.path.getsize(f) for f in voice_files)

    logger.info(f"Before filtering: {total_files_before} files, {total_size_before} bytes")
    logger.info(f"After filtering: {total_files_after} files, {total_size_after} bytes")

    logger.info("Cloning voice...")
    voice = clone(
        name=voice_name,
        description=description,
        files=voice_files,
    )

    logger.info("Generating audio...")
    audio = generate("this is a test, how do I sound?", voice=voice)

    logger.info("Saving audio...")
    save(audio, "./output.mp3")

    # End timing and print elapsed time
    end_time = time.time()
    logger.info(f"Completed in {end_time - start_time} seconds.")

if __name__ == "__main__":
    # video_urls = [
    #     "https://www.youtube.com/watch?v=pWbSl7d0tEc", # https://www.youtube.com/watch?v=pWbSl7d0tEc
    #     "https://www.youtube.com/watch?v=WRW7eY6K4Jo", # They lied to you: Why Punishment DOESN'T WORK..
    #     "https://www.youtube.com/watch?v=FNJpJG-sSXM", # Biden's tax plan.....
    #     "https://www.youtube.com/watch?v=-Pz0NpcILOY", # increased wealth EXPONENTIALLY
    #     "https://www.youtube.com/watch?v=RBR4BwOVNvs", # solved everything
    #     "https://www.youtube.com/watch?v=YaNX49ygr0I", # how to get what you want
    #     "https://www.youtube.com/watch?v=Ec41cSp_tWc", # why direct response marketers get rich not wealth
    #     "https://www.youtube.com/watch?v=kW2vDMAmlPI", # $100M CEO: How I know who to trust...
    #     "https://www.youtube.com/watch?v=_gcqwupsza8", # I sold my company for $46,200,000 at age 32...7 LESSONS I learned..
    #     "https://www.youtube.com/watch?v=o7R_K6LwKNk", # $100M CEO: "Why therapists failed me..." [language warning]
    #     "https://www.youtube.com/watch?v=o7R_K6LwKNk", # $100M CEO: "Why therapists failed me..." [language warning]
    #     "https://www.youtube.com/watch?v=F3NyhOtRpOE", # $100M CEO explains: How to CREATE a $100,000,000 product..[leaked training]
    #     "https://www.youtube.com/watch?v=w5g0JiO7OdE", # I paid 0% tax on 56% of my income...here's how..
    #     "https://www.youtube.com/watch?v=pWbSl7d0tEc", # I sold 8 businesses by age 32 [here’s how]
    #     "https://www.youtube.com/watch?v=oi7bnS8uyJM", # 30 Minutes of sales training that will explode your business in 2022
    #     "https://www.youtube.com/watch?v=3P1XjUvo1b4", # I cracked Starbucks RECURRING SALES model and built a FORTUNE...
    #     "https://www.youtube.com/watch?v=_qspvJAq34M", # How I got 700 people to pay me $40,000 each...no bs..
    #     "https://www.youtube.com/watch?v=kULFeI3LRYk", # I SPENT $100,000 on courses, so you don't have to...
    #     "https://www.youtube.com/watch?v=C_SgvSvJZdk", # 8 Lessons Charlie Munger Taught Me To Build $112M Business
    #     "https://www.youtube.com/watch?v=Q2VUuUGfpNY", # 6 Hacks To Make More Money [Increase LTV] Without More Customers
    #     "https://www.youtube.com/watch?v=4LeHKDGmEIQ", # This is Why You're Not Happy - Eye Opening
    #     "https://www.youtube.com/watch?v=Fy8XX8EuEnA", # I Made $31,714,980 in 2020 (Here's What I Learned)
    #     "https://www.youtube.com/watch?v=cemduJKQl5w", # Recruiting and Hiring Tips - How to Hire The Best Employees
    #     "https://www.youtube.com/watch?v=kULFeI3LRYk", # I SPENT $100,000 on courses, so you don't have to...
    #  ]  
    # video_urls = [
    #     "https://www.youtube.com/watch?v=60_7PU9JDIw", # I Convinced 10,000 People To Promote My Book For Me (For Free)
    #     "https://www.youtube.com/watch?v=5cOwh-8scu8", # Make Money Online (Without Destroying Your Reputation)
    #     "https://www.youtube.com/watch?v=7NMH1oAkgLY", # Giving Away Free Stuff Will Make You Rich
    #     "https://www.youtube.com/watch?v=lJF__n_34ew", # My 12 Hour Work Day (in 15 Minutes)
    #     "https://www.youtube.com/watch?v=Nh8Oc7ERdIU", # How to Get Ahead of 99% of People
    #     "https://www.youtube.com/watch?v=zZyRg4Fzabk", # HUGE ANNOUNCEMENT
    #     "https://www.youtube.com/watch?v=VPre_XMgKjs", # Why MrBeast Will be Worth $100 Billion
    #     "https://www.youtube.com/watch?v=YFA8AS5Cu2w", # watch this if you're tired of being broke
    #     "https://www.youtube.com/watch?v=1taVrxMFjaY&t=179s", # NO NEW FRIENDS (My "Extreme Views" on Friendship)
    #     "https://www.youtube.com/watch?v=9gVdCR7W8o8", # The REAL Reason Your Business Isn't Growing
    #     "https://www.youtube.com/watch?v=6ySRKgXBcO0&t=925s", # Day In The Life of Alex Hormozi
    #     "https://www.youtube.com/watch?v=fxyhIXZ6Yog", # The Alex Hormozi Diet (REVEALED)
    #     "https://www.youtube.com/watch?v=oTQPxPFROck&t=289s", # How to Build a LEGIT Online Course (2023)
    #     "https://www.youtube.com/watch?v=KQuyQpFANpA", # I Solved Three $100,000,000 Business Problems
    #     "https://www.youtube.com/watch?v=qLM5G7N3l3I", # 3 Ways to Do What You Love (and get wealthy too)
    #     "https://www.youtube.com/watch?v=SYkwtqFoRcM", # How to go ALL IN on your side hustle..
    #     "https://www.youtube.com/watch?v=zBZHWrvjD8Y", # How I Set Goals That ACTUALLY MAKE MONEY
    #     "https://www.youtube.com/watch?v=LVM89ik-7Kw", # "I'm Broke, What Should I Sell?"
    #     "https://www.youtube.com/watch?v=ueJg14gQLuc", # The SEASON OF NO (What it Takes to Win)
    #     "https://www.youtube.com/watch?v=vZfatNSouDQ&t=179s", # Hardcore Business Lessons I Learned From A Dealer
    #     "https://www.youtube.com/watch?v=zNJ5JzEJgyo", # Why You Shouldn't Copy Me
    #     "https://www.youtube.com/watch?v=_PCCqqv2pig", # HOW TO GET WHAT YOU WANT (6 Proven Methods)
    #     "https://www.youtube.com/watch?v=BHMeYaHEMpc", # How to Grow ANY Local Business (my framework)
    #     "https://www.youtube.com/watch?v=ULGT0Qpglek&t=624s", # 17 Conversations That Made Me A Millionaire
    #     "https://www.youtube.com/watch?v=-wnnwCqGeNc", # The #1 Reason Young People Stay Poor
    #     "https://www.youtube.com/watch?v=0mqqbuM9sAk", # I Built 4 Businesses In A Row To Show It's Not Luck
    #     "https://www.youtube.com/watch?v=ONV__y1z7MI", # How The World’s RICHEST Man Made His Money
    # ]
    video_urls = [
        "https://www.youtube.com/watch?v=5cOwh-8scu8", # Make Money Online (Without Destroying Your Reputation)
    ]

    voice_name = "hormozi_test"
    filename = "hormozi_test"

    main(video_urls, voice_name, filename)
