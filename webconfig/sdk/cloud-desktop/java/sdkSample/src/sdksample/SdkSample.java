/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package sdksample;

import vd.remote.rvdHttpClient;

public class SdkSample {
    public static void main(String[] args) {
        rvdHttpClient hc = new rvdHttpClient();
        hc.setHost("192.168.96.122", 8000);
        hc.setUser("wangfeng", "11111111");
        Boolean ret = hc.logon();
        return;
    }
}
