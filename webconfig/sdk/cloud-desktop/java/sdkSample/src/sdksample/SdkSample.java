/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package sdksample;

import java.io.File;
import java.io.IOException;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import vd.remote.rvdHttpClient;

public class SdkSample {
    public static void runShellCmd(String cmd_line) {
        try {
            Process p;
            p = Runtime.getRuntime().exec(cmd_line);
            p.waitFor();
        } catch (IOException | InterruptedException ex) {
            Logger.getLogger(SdkSample.class.getName()).log(Level.SEVERE, null, ex);
        }
    }
    
    public static String getRDPComand() {
        if (File.separator.equals("/")) {
            return "/usr/local/bin/rdesktop %s";
        } else {
            return "mstsc /f zv:%s";
        }
    }
    
    public static void main(String[] args) {
        JSONObject response;
        String tmpresult, phase, state;
        Boolean flag;
        String rdp_cmd_line;
        long progress = 0;
        
        rvdHttpClient hc = new rvdHttpClient();
        hc.setHost("192.168.96.124", 8000);
        //hc.setHost("10.0.0.21", 8000);
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
        phase = (String)((JSONObject)vmobj).get("phase");
        state = (String)((JSONObject)vmobj).get("state");
        
        if (phase.equals("editing")) {
            if (state.equals("running") || state.equals("Running")) {
               response = hc.getRDPUrl((JSONObject)vmobj);
               tmpresult = (String)response.get("Result");
               if (tmpresult.equals("FAIL")) {
                   System.out.println((String)response.get("error"));
                   System.exit(-1);
               } else {
                   rdp_cmd_line = getRDPComand();
                   rdp_cmd_line = String.format(rdp_cmd_line, (String)response.get("mgr_url"));
                   runShellCmd(rdp_cmd_line);
                   System.exit(0);
               }
            }
        }
        
        response = hc.startVM((JSONObject)vmobj);
        tmpresult = (String)response.get("Result");
        if (tmpresult.equals("FAIL")) {
            hc.errorHandle((JSONObject)vmobj);
            System.out.println((String)response.get("error"));
            System.exit(-1);
        }
        
        response = hc.prepareVM((JSONObject)vmobj);
        tmpresult = (String)response.get("Result");
        if (tmpresult.equals("FAIL")) {
            hc.errorHandle((JSONObject)vmobj);
            System.out.println((String)response.get("error"));
            System.exit(-1);
        }
        
        flag = true;
        while (flag) {
            try {
                Thread.sleep(2000);
                response = hc.getPrepareProgress((JSONObject)vmobj);
                
                phase = (String)response.get("phase");
                state = (String)response.get("state");
                if (phase.equals("preparing") && state.equals("done")) {
                    flag = false;
                }
                progress = (long)response.get("progress");
                System.out.println("current progress is " + progress);
                
            } catch (InterruptedException ex) {
                Logger.getLogger(SdkSample.class.getName()).log(Level.SEVERE, null, ex);
            }
        }
        
        response = hc.runVM((JSONObject)vmobj);
        tmpresult = (String)response.get("Result");
        if (tmpresult.equals("FAIL")) {
            hc.errorHandle((JSONObject)vmobj);
            System.out.println((String)response.get("error"));
            System.exit(-1);
        }
        
        flag = true;
        while (flag) {
            try {
                Thread.sleep(2000);
                response = hc.getVMStatus((JSONObject)vmobj);
                
                state = (String)response.get("state");
                if (state.equals("Running") || state.equals("running")) {
                    flag = false;
                    System.out.println("VM is running, now can display it.");
                }
                
            } catch (InterruptedException ex) {
                Logger.getLogger(SdkSample.class.getName()).log(Level.SEVERE, null, ex);
            }
        }
        
        response = hc.getRDPUrl((JSONObject)vmobj);
        tmpresult = (String)response.get("Result");
        if (tmpresult.equals("FAIL")) {
            System.out.println((String)response.get("error"));
            System.exit(-1);
        }
        
        rdp_cmd_line = getRDPComand();
        rdp_cmd_line = String.format(rdp_cmd_line, (String)response.get("mgr_url"));
        runShellCmd(rdp_cmd_line);
    }
}

