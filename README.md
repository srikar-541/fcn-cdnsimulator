# fcn5

RUN make dnsserver httpserver 
to make the files.


Q. Briefly describe the design decisions you are making in your DNS server and HTTP server:

The DNS server is very straight forward, and for the current scope of the project calls socket.gethostbyname on the question and responds with an appropriate DNS response message.
Ideally, for every client IP there should be an entry in a table which specified the IP of the best replica server.

The http server accepts the port number on which the socket has to be bound and the origin server from which the resource has to be fetched.

If the request origin isn’t cs5700cdnproject.ccs.neu.edu, we simply display an error message.
We have also put a constraint that the port number can be between 40000-65535

If a client requests for the resource by doing a curl/wget/hitting on the browser, we first check to see if there is a file by name ’cache’ in the local directory. 
If it’s not present, we do a get request of that resource from the origin server. This file will be cached as ‘cache’ file in the same directory. 
For further requests, the http server directly returns the data stored in this ‘cache’ instead of fetching it from the origin server.

If the resource that the client requested is other than localhost:port_number/index.html, we simply return a http 404 not found in the http headers of the response.

Q. How would you change your DNS server to dynamically return an IP, instead of a hard coded IP?

The DNS server precomputes the best replica server IP for a given client and returns it when a request is made. 
The best replica is decided based on factors such as client location, server load and Network conditions. 
A short TTL for the best replica server will limit the effect of caching.

Q. Explain how you would implement the mapping of incoming client requests to CDN servers, if you had several servers to pick from. 
Notice the CDN servers are geographically distributed, and so are clients. Be specific about what kind of measurement system you would implement, 
where exactly the data would be collected, and how you would then decide which server is the best option for a particular client.


CDNs need a way to send clients to the “best” server The best server can change over time.
And this depends on client location, network conditions, server load etc

Taking into account these parameters, we plan to implement the mapping as follows:

We plan to use another anycast server that computes the best replica server for each client and sends regular updates to the DNS server. 

So the DNS server at any point of time has a record for every client IP and the IP of the best replica server.

The replica servers report two parameters to this server - RTT of the connection between the replica and a client, and the current number of requests it is handling every minute. 
The report message could look like:
{Client IP: 101.10.1.01, RTT: 89ms, RPM: 90}

The server uses this information to compute best replica server for every client.

When a new Client contacts the DNS server, the anycast server creates an entry in its table 

Once a client requesting service for the first time, DNS will create a record for this client which contains the client ip and a list of tuples corresponding to each 
replica server. This tuple contains 4 parameters ie replica id, RTT(0 initially), TTL, RPM(0 initially). 
The record's format is as follows:

{Client IP, {CDN 1, 0, TTL, 0}, {CDN 2, 0, TTL, 0}, {CDN 3, 0, TTL, 0}}

Initially, all the RTT are set to be 0.
After initializing these entries for this client, DNS picks the first CDN which should be CDN 1 to respond client. 
In a round robin fashion, each of the replica servers are reported to the DNS till all values of RTT and RPM are collected. 
After that the best replica server for a client is computed by taking the replica with the least RTT.

Additionally the RPM value is checked against a threshold value to ensure load balancing. If the RPM value exceeds the threshold, the server simply reports the server with the next best RTT value.

Each of these entries have a TTL, if it expires, the RTT and RPM are set to zero, and the next best server is returned. 
Setting the RPM and RTT to zero will ensure that this server will be picked next time and the server will report fresh values of RTT and RPM.


Q: Explain how you would implement caching for your HTTP server, if we were to send a range of requests to your HTTP server. 
What cache replacement strategy would you implement if content popularity followed a Zipfian distribution. 
How would your HTTP server respond to a request for a content that is not currently in the cache. 

LRU cache implementation can be used if the content popularity follows a Zipfian distribution because the resource that was used the least will most probably not be requested again in near future, hence it can be evicted from the cache. 
This algorithm requires keeping track of what was used when.

Implementation details:

Each time a client sends a request to the CDN, CDN will check its local cache to see if that file exists. 
If it exists, CDN will respond with that file and remove that from the queue and put it to the end of the queue meaning it was used most recently and might be used again.
If that file doesn't exist, CDN will send request to the origin server for that file. If the origin server responds with 200 code, CDN will put the new resource at the end of CDN cache queue.
If the origin server responds with status code other than 200, the CDN will do nothing but send the response as is back to the client.

# p5final
