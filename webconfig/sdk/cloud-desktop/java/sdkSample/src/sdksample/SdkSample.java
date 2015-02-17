/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package sdksample;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import vd.remote.rvdHttpClient;

public class SdkSample {
    public static void main(String[] args) {
        rvdHttpClient hc = new rvdHttpClient();
        //hc.setHost("192.168.96.122", 8000);
        hc.setHost("10.0.0.21", 8000);
        hc.setUser("wangfeng", "11111111");
        
        Boolean ret = hc.logon();
        
        if (ret == false) {
            System.out.println("logon failed, try correct user name & password");
            System.exit(-1);
        }
        
        JSONObject list_vms;
        list_vms = hc.getVDList();
        JSONArray  array_vms = (JSONArray)list_vms.get("data");
        
        Object vmobj = array_vms.get(0);
        String phase = (String)((JSONObject)vmobj).get("phase");
        String state = (String)((JSONObject)vmobj).get("state");
        
        if (phase.equals("editing")) {
            if (state.equals("running") || state.equals("Running")) {
               
            }
        }
         
    }
}

