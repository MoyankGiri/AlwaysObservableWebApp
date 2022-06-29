from sqlalchemy import false
import workload_simulator

#workload_simulator.createBlog_variedLengths('http://localhost:5000/createBlog',0,MAXPOSTS = 5)
workload_simulator.make_get_request('http://localhost:5000/login',{'bool':False})