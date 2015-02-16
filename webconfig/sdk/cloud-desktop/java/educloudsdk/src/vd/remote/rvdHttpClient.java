/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
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
    private String remove_task_url; 
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
        remove_task_url = "clc/api/1.0/tasks/delete";
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
    
    public Boolean logon() {
        String url = String.format("http://%s:%d/%s", host_IP, host_port, login_url);
        
        try {
            String myret = Request.Post(url).bodyForm(Form.form().add("email", user_id).add("password", user_password).build()).execute().returnContent().asString();
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

}
