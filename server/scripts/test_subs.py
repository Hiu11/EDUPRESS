import httpx
import re
import json

def fetch_subs(video_id):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    url = f'https://www.youtube.com/watch?v={video_id}'
    with httpx.Client(timeout=10.0) as client:
        res = client.get(url, headers=headers)
        if res.status_code != 200:
            print("Failed to fetch page")
            return
            
        match = re.search(r'ytInitialPlayerResponse\s*=\s*({.+?});var', res.text)
        if not match:
            print("Could not find ytInitialPlayerResponse")
            return
            
        data = json.loads(match.group(1))
        
        try:
            tracks = data['captions']['playerCaptionsTracklistRenderer']['captionTracks']
            first_track_url = tracks[0]['baseUrl']
            
            # append tlang=vi
            if '?' in first_track_url:
                vi_url = first_track_url + '&tlang=vi&fmt=json3'
            else:
                vi_url = first_track_url + '?tlang=vi&fmt=json3'
                
            sub_res = client.get(vi_url, headers=headers)
            print("Sub HTTP status:", sub_res.status_code)
            sub_data = sub_res.json()
            
            print("Sub events count:", len(sub_data.get('events', [])))
            print(sub_data['events'][0])
            
        except Exception as e:
            print("Error parsing tracks:", e)

if __name__ == '__main__':
    fetch_subs('pTB0EiLXUC8')
