
# DEPENDECIAS
%pip3 install obs-websocket-py #to control obs
%pip3 install paramiko #for ssh and sftp
%brew install ffmpeg #to convert files into mp4 if necessary

# In[ ]:


def printTotals(downloaded, toBeDownloaded):
    print("Downloaded: {0}\tOut of: {1}".format(downloaded, toBeDownloaded))


# In[ ]:


import threading
from obswebsocket import obsws, requests
import paramiko as pmk
import subprocess

def recording(client, hostname, username, password, event_start, event_stop, barrier):
    sshClient = pmk.SSHClient()
    sshClient.set_missing_host_key_policy(pmk.AutoAddPolicy())
    sshClient.connect(hostname, username=username, password=password)
    sftpClient = sshClient.open_sftp()
    client.connect()
    event_start.wait()  
    print(f"Recording started on {hostname}")  
    client.call(requests.StartRecord())
    event_stop.wait()  
    response = client.call(requests.StopRecord())
    print(f"Recording stopped on {hostname}")
    while True: 
        recordStatus = client.call(requests.GetRecordStatus())
        if recordStatus.datain['outputActive'] == False:
            break
    
    out_name = response.datain['outputPath'].split("/")[-1]
    sftpClient.get(response.datain['outputPath'], out_name, callback=printTotals) #Aqui se bloqea el hilo hasta que se descargue el archivo
    sftpClient.close()
    sshClient.close()
    client.disconnect()
    
    try:
        mkv = out_name 
        output_name = out_name + ".mp4"  
        

        subprocess.run(
            ["ffmpeg", "-i", f"./{mkv}", "-codec", "copy", f"./{output_name}"],
            check=True
        )#Convert to mp4, can be commented
    except subprocess.CalledProcessError as e:
        print("Error:", e)
    
    barrier.wait() 

def main():
    hostnames = [""]  # Here, IP's of the computers 
    usernames = [""] #Usernames of the computers
    passwords = [""] #ssh passwords
    clients = [obsws(hostname, 4455) for hostname in hostnames]

    barrier = threading.Barrier(len(hostnames) + 1) 

    event_start = threading.Event()
    event_stop = threading.Event()

    threads = []

    for client, username, password, hostname in zip(clients, usernames, passwords, hostnames):
        thread = threading.Thread(target=recording, args=(client, hostname, username, password, event_start, event_stop, barrier))
        threads.append(thread)
        thread.start()

    
    input("Press 's' to start recording\n")
    event_start.set()

    
    input("Press 'q' to stop recording\n")
    event_stop.set()

    barrier.wait()

    for thread in threads:
        thread.join()

    

if __name__ == "__main__":
    main()

