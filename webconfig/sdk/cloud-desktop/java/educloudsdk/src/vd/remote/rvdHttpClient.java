package vd.remote;

import java.io.IOException;
import org.apache.http.client.fluent.Form;
import org.apache.http.client.fluent.Request;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

/**
 *
 * @author luhya
 */
public class rvdHttpClient {
    private String seesionID;
    private String host_IP;
    private int    host_port;
    private String user_id;
    private String user_password;
    
    private String login_url; 
    private String list_vm;  
    private String create_url; 
    private String start_url;  
    private String prepare_url; 
    private String progress_url;
    private String run_url; 
    private String stop_url;
    private String vmstatus_url; 
    private String rdp_url;
    private String del_vm_url;
    
    public rvdHttpClient() {
        seesionID       = "";
        host_IP         = "";
        host_port       = 80;
        user_id         = "";
        user_password   = "";
    
        login_url       = "clc/api/1.0/user_login";
        list_vm         = "clc/api/1.0/list_myvds";
        create_url      = "clc/api/1.0/rvd/create";
        start_url       = "clc/api/1.0/rvd/start";
        prepare_url     = "clc/api/1.0/rvd/prepare";
        progress_url    = "clc/api/1.0/rvd/getprogress";
        run_url         = "clc/api/1.0/rvd/run";
        stop_url        = "clc/api/1.0/rvd/stop";
        vmstatus_url    = "clc/api/1.0/rvd/getvmstatus";
        rdp_url         = "clc/api/1.0/rvd/get_rdp_url";
        del_vm_url      = "clc/api/1.0/tasks/delete";
    }
    
    public void setHost(String ip, int port) {
        host_IP     = ip;
        host_port   = port;
    }
    
    public void setUser(String uid, String pwd) {
        user_id         = uid;
        user_password   = pwd;
    }
    
    /*
    return : true or false
    */
    public Boolean logon() {
        String url = String.format("http://%s:%d/%s", host_IP, host_port, login_url);
        
        try {
            String myret = Request.Post(url).bodyForm(Form.form().
                    add("email", user_id).
                    add("password", user_password).build()).
                    execute().returnContent().asString();
            JSONParser parser=new JSONParser();
            Object myobj = parser.parse(myret);
            JSONObject response = (JSONObject)myobj;
            String result = (String) response.get("status");
            if (result.equals("SUCCESS")) {
                seesionID  = (String) response.get("sid");
                return true;
            } else {
                return false;
            }
        } catch (Exception pe) {
            return false;
        }
    }
    
    /*
    # if sucess, return as belwo
    # {
    #   'Result' : 'OK',
    #   'data'   : list of vms
    # }
    #
    # each vm in list looks like  below:
    # {
    #   'ecid'      : 'image id',
    #   'name'      : 'image name',
    #   'ostype'    : 'image os type',
    #   'desc'      : 'image description',
    #   'tid'       : 'transaction id',
    #   'phase'     : 'transaction phase',
    #   'state'     : 'transaction state',
    #   'mgr_url'   : 'RDP access ip:port'
    #   'id'        : 'index in list'
    # }
    #
    # if error, return as below
    # {
    #   'Result' : 'Failed',
    #   'error'  : 'error message'
    # }
    */
    public JSONObject getVDList() {
        String url = String.format("http://%s:%d/%s", host_IP, host_port, list_vm);
        
        try {
            String myret = Request.Post(url).bodyForm(Form.form().
                    add("user", user_id).
                    add("sid",  seesionID).
                    build()).execute().returnContent().asString();
            
            JSONParser parser=new JSONParser();
            Object myobj = parser.parse(myret);
            JSONObject response = (JSONObject)myobj;
            return response;
        } catch (Exception pe) {
            JSONObject except_ret = new JSONObject();
            return except_ret;
        }
    }
    
    /*
    ##
    ## return :
    ##   sucess :  ['Result': 'OK',    'tid'   : tid]
    ##   failed :  ['Result': 'FAIL',  'error' : error msg]
    ##
    */
    public JSONObject _create_tvd(JSONObject vmdata) {
        String url = String.format("http://%s:%d/%s/%s", host_IP, host_port, create_url, (String)vmdata.get("ecid"));
        
        try {
            String myret = Request.Post(url).bodyForm(Form.form().
                    add("sid",  seesionID).
                    build()).execute().returnContent().asString();
            
            JSONParser parser=new JSONParser();
            Object myobj = parser.parse(myret);
            JSONObject response = (JSONObject)myobj;
            return response;
        } catch (IOException | ParseException pe) {
            JSONObject except_ret = new JSONObject();
            return except_ret;
        }
    }
    
    /*
    ##
    ## return :
    ##   sucess :  ['Result': 'OK',    'tid'   : tid]
    ##   failed :  ['Result': 'FAIL',  'error' : error msg]
    ##
    */
    public JSONObject _start_tvd(JSONObject vmdata) {
        String tid = (String)vmdata.get("tid");
        String[] tidArray = _parseTID(tid);
        
        String url = String.format("http://%s:%d/%s/%s/%s/%s", 
                host_IP, host_port, start_url, tidArray[0], tidArray[1], tidArray[2]);
        
        try {
            String myret = Request.Post(url).bodyForm(Form.form().
                    add("sid",  seesionID).
                    build()).execute().returnContent().asString();
            
            JSONParser parser=new JSONParser();
            Object myobj = parser.parse(myret);
            JSONObject response = (JSONObject)myobj;
            return response;
        } catch (IOException | ParseException pe) {
            JSONObject except_ret = new JSONObject();
            return except_ret;
        }
    }
    
    public String[]  _parseTID(String tid) {
        return tid.split(":");
    }
    
    public JSONObject startVM(JSONObject vmdata) {
        String tid = (String)vmdata.get("tid");
        if (tid.equals("")) {
            return _create_tvd(vmdata);
        } else {
            return _start_tvd(vmdata);
        }
    }
    
    /*
    ##
    ## return :
    ##   sucess :  ['Result': 'OK',    'tid'   : tid]
    ##
    */
    public JSONObject stopVM(JSONObject vmdata) {
        String tid = (String)vmdata.get("tid");
        String[] tidArray = _parseTID(tid);
        
        String url = String.format("http://%s:%d/%s/%s/%s/%s", 
                host_IP, host_port, stop_url, tidArray[0], tidArray[1], tidArray[2]);
        
        try {
            String myret = Request.Post(url).bodyForm(Form.form().
                    add("sid",  seesionID).
                    build()).execute().returnContent().asString();
            
            JSONParser parser=new JSONParser();
            Object myobj = parser.parse(myret);
            JSONObject response = (JSONObject)myobj;
            return response;
        } catch (IOException | ParseException pe) {
            JSONObject except_ret = new JSONObject();
            return except_ret;
        }
    }
    
    /*
    ##
    ## return :
    ##   sucess :  ['Result': 'OK',    'tid'   : tid]
    ##   failed :  ['Result': 'FAIL',  'error' : error msg]
    ##
    */
    public JSONObject prepareVM(JSONObject vmdata) {
        String tid = (String)vmdata.get("tid");
        String[] tidArray = _parseTID(tid);
        
        String url = String.format("http://%s:%d/%s/%s/%s/%s", 
                host_IP, host_port, prepare_url, tidArray[0], tidArray[1], tidArray[2]);
        
        try {
            String myret = Request.Post(url).bodyForm(Form.form().
                    add("sid",  seesionID).
                    build()).execute().returnContent().asString();
            
            JSONParser parser=new JSONParser();
            Object myobj = parser.parse(myret);
            JSONObject response = (JSONObject)myobj;
            return response;
        } catch (IOException | ParseException pe) {
            JSONObject except_ret = new JSONObject();
            return except_ret;
        }
    }
    
    /*
    ##
    ##  return = {
    ##    'type': 'taskstatus',
    ##    'phase': "preparing",
    ##    'state': 'downloading',
    ##    'progress': 0,
    ##    'tid': tid,
    ##    'prompt': '',
    ##    'errormsg': '',
    ##    'failed' : 0
    ##  }
    ##
    */
    public JSONObject getPrepareProgress(JSONObject vmdata) {
        String tid = (String)vmdata.get("tid");
        String[] tidArray = _parseTID(tid);
        
        String url = String.format("http://%s:%d/%s/%s/%s/%s", 
                host_IP, host_port, progress_url, tidArray[0], tidArray[1], tidArray[2]);
        
        try {
            String myret = Request.Post(url).bodyForm(Form.form().
                    add("sid",  seesionID).
                    build()).execute().returnContent().asString();
            
            JSONParser parser=new JSONParser();
            Object myobj = parser.parse(myret);
            JSONObject response = (JSONObject)myobj;
            return response;
        } catch (IOException | ParseException pe) {
            JSONObject except_ret = new JSONObject();
            return except_ret;
        }
    }
    
    /*
    ##
    ## return :
    ##   sucess :  ['Result': 'OK',    'tid'   : tid]
    ##
    */
    public JSONObject runVM(JSONObject vmdata) {
        String tid = (String)vmdata.get("tid");
        String[] tidArray = _parseTID(tid);
        
        String url = String.format("http://%s:%d/%s/%s/%s/%s", 
                host_IP, host_port, run_url, tidArray[0], tidArray[1], tidArray[2]);
        
        try {
            String myret = Request.Post(url).bodyForm(Form.form().
                    add("sid",  seesionID).
                    build()).execute().returnContent().asString();
            
            JSONParser parser=new JSONParser();
            Object myobj = parser.parse(myret);
            JSONObject response = (JSONObject)myobj;
            return response;
        } catch (IOException | ParseException pe) {
            JSONObject except_ret = new JSONObject();
            return except_ret;
        }
    }
    
    /*
    ##
    ##  return = {
    ##        'type'    : 'taskstatus',
    ##        'phase'  : "editing",
    ##        'state'  : 'stopped', 'booting', 'running' ,
    ##        'tid'    : _tid,
    ##        'failed' : 0
    ##  }
    ##
    */
    public JSONObject getVMStatus(JSONObject vmdata) {
        String tid = (String)vmdata.get("tid");
        String[] tidArray = _parseTID(tid);
        
        String url = String.format("http://%s:%d/%s/%s/%s/%s", 
                host_IP, host_port, vmstatus_url, tidArray[0], tidArray[1], tidArray[2]);
        
        try {
            String myret = Request.Post(url).bodyForm(Form.form().
                    add("sid",  seesionID).
                    build()).execute().returnContent().asString();
            
            JSONParser parser=new JSONParser();
            Object myobj = parser.parse(myret);
            JSONObject response = (JSONObject)myobj;
            return response;
        } catch (IOException | ParseException pe) {
            JSONObject except_ret = new JSONObject();
            return except_ret;
        }
    }
    
    /*
    ##
    ## return :
    ##   sucess :  ['Result': 'OK',    'mgr_url'   : rdp url]
    ##
    */
    public JSONObject getRDPUrl(JSONObject vmdata) {
        String tid = (String)vmdata.get("tid");
        String[] tidArray = _parseTID(tid);
        
        String url = String.format("http://%s:%d/%s/%s/%s/%s", 
                host_IP, host_port, rdp_url, tidArray[0], tidArray[1], tidArray[2]);
        
        try {
            String myret = Request.Post(url).bodyForm(Form.form().
                    add("sid",  seesionID).
                    build()).execute().returnContent().asString();
            
            JSONParser parser=new JSONParser();
            Object myobj = parser.parse(myret);
            JSONObject response = (JSONObject)myobj;
            return response;
        } catch (IOException | ParseException pe) {
            JSONObject except_ret = new JSONObject();
            return except_ret;
        }
    }
    
    public JSONObject delet_vm(JSONObject vmdata) {
        String tid = (String)vmdata.get("tid");
        String[] tidArray = _parseTID(tid);
        
        String url = String.format("http://%s:%d/%s/%s/%s/%s", 
                host_IP, host_port, del_vm_url, tidArray[0], tidArray[1], tidArray[2]);
        
        try {
            String myret = Request.Post(url).bodyForm(Form.form().
                    add("tid",  tid).
                    build()).execute().returnContent().asString();
            
            JSONParser parser=new JSONParser();
            Object myobj = parser.parse(myret);
            JSONObject response = (JSONObject)myobj;
            return response;
        } catch (IOException | ParseException pe) {
            JSONObject except_ret = new JSONObject();
            return except_ret;
        }
    }
    
    public JSONObject errorHandle(JSONObject vmdata) {
        return delet_vm(vmdata);
    }
}
