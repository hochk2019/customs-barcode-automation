<?xml version="1.0"?>
<configuration>
    <configSections>
        <sectionGroup name="applicationSettings" type="System.Configuration.ApplicationSettingsGroup, System, Version=2.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089">
            <section name="TSD.ECUSKDNET.My.MySettings" type="System.Configuration.ClientSettingsSection, System, Version=2.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089" requirePermission="false"/>
        </sectionGroup>
    </configSections>
    <system.diagnostics>
        <sources>
            <!-- This section defines the logging configuration for My.Application.Log -->
            <source name="DefaultSource" switchName="DefaultSwitch">
                <listeners>
                    <add name="FileLog"/>
                    <!-- Uncomment the below section to write to the Application Event Log -->
                    <!--<add name="EventLog"/>-->
                </listeners>
            </source>
        </sources>
        <switches>
            <add name="DefaultSwitch" value="Information"/>
        </switches>
        <sharedListeners>
            <add name="FileLog" type="Microsoft.VisualBasic.Logging.FileLogTraceListener, Microsoft.VisualBasic, Version=8.0.0.0, Culture=neutral, PublicKeyToken=b03f5f7f11d50a3a, processorArchitecture=MSIL" initializeData="FileLogWriter"/>
            <!-- Uncomment the below section and replace APPLICATION_NAME with the name of your application to write to the Application Event Log -->
            <!--<add name="EventLog" type="System.Diagnostics.EventLogTraceListener" initializeData="APPLICATION_NAME"/> -->
        </sharedListeners>
    </system.diagnostics>
    <system.serviceModel>
        <bindings>
            <basicHttpBinding>
                <binding name="ServiceSoap1" closeTimeout="00:01:00" openTimeout="00:01:00" receiveTimeout="00:10:00" sendTimeout="00:01:00" allowCookies="false" bypassProxyOnLocal="false" hostNameComparisonMode="StrongWildcard" maxBufferSize="65536" maxBufferPoolSize="524288" maxReceivedMessageSize="65536" messageEncoding="Text" textEncoding="utf-8" transferMode="Buffered" useDefaultWebProxy="true">
                    <readerQuotas maxDepth="32" maxStringContentLength="8192" maxArrayLength="16384" maxBytesPerRead="4096" maxNameTableCharCount="16384"/>
                    <security mode="Transport">
                        <transport clientCredentialType="None" proxyCredentialType="None" realm=""/>
                        <message clientCredentialType="UserName" algorithmSuite="Default"/>
                    </security>
                </binding>
                <binding name="ServiceSoap2" closeTimeout="00:01:00" openTimeout="00:01:00" receiveTimeout="00:10:00" sendTimeout="00:01:00" allowCookies="false" bypassProxyOnLocal="false" hostNameComparisonMode="StrongWildcard" maxBufferSize="65536" maxBufferPoolSize="524288" maxReceivedMessageSize="65536" messageEncoding="Text" textEncoding="utf-8" transferMode="Buffered" useDefaultWebProxy="true">
                    <readerQuotas maxDepth="32" maxStringContentLength="8192" maxArrayLength="16384" maxBytesPerRead="4096" maxNameTableCharCount="16384"/>
                    <security mode="None">
                        <transport clientCredentialType="None" proxyCredentialType="None" realm=""/>
                        <message clientCredentialType="UserName" algorithmSuite="Default"/>
                    </security>
                </binding>
                <binding name="CISServiceSoap" closeTimeout="00:01:00" openTimeout="00:01:00" receiveTimeout="00:10:00" sendTimeout="00:01:00" allowCookies="false" bypassProxyOnLocal="false" hostNameComparisonMode="StrongWildcard" maxBufferSize="65536" maxBufferPoolSize="524288" maxReceivedMessageSize="65536" messageEncoding="Text" textEncoding="utf-8" transferMode="Buffered" useDefaultWebProxy="true">
                    <readerQuotas maxDepth="32" maxStringContentLength="8192" maxArrayLength="16384" maxBytesPerRead="4096" maxNameTableCharCount="16384"/>
                    <security mode="None">
                        <transport clientCredentialType="None" proxyCredentialType="None" realm=""/>
                        <message clientCredentialType="UserName" algorithmSuite="Default"/>
                    </security>
                </binding>
                <binding name="KDTServiceSoap" closeTimeout="00:01:00" openTimeout="00:01:00" receiveTimeout="00:10:00" sendTimeout="00:01:00" allowCookies="false" bypassProxyOnLocal="false" hostNameComparisonMode="StrongWildcard" maxBufferSize="65536" maxBufferPoolSize="524288" maxReceivedMessageSize="65536" messageEncoding="Text" textEncoding="utf-8" transferMode="Buffered" useDefaultWebProxy="true">
                    <readerQuotas maxDepth="32" maxStringContentLength="8192" maxArrayLength="16384" maxBytesPerRead="4096" maxNameTableCharCount="16384"/>
                    <security mode="None">
                        <transport clientCredentialType="None" proxyCredentialType="None" realm=""/>
                        <message clientCredentialType="UserName" algorithmSuite="Default"/>
                    </security>
                </binding>
                <binding name="ServiceSoap" closeTimeout="00:01:00" openTimeout="00:01:00" receiveTimeout="00:10:00" sendTimeout="00:01:00" allowCookies="false" bypassProxyOnLocal="false" hostNameComparisonMode="StrongWildcard" maxBufferSize="65536" maxBufferPoolSize="524288" maxReceivedMessageSize="65536" messageEncoding="Text" textEncoding="utf-8" transferMode="Buffered" useDefaultWebProxy="true">
                    <readerQuotas maxDepth="32" maxStringContentLength="8192" maxArrayLength="16384" maxBytesPerRead="4096" maxNameTableCharCount="16384"/>
                    <security mode="None">
                        <transport clientCredentialType="None" proxyCredentialType="None" realm=""/>
                        <message clientCredentialType="UserName" algorithmSuite="Default"/>
                    </security>
                </binding>
                <binding name="ServiceSoap3" closeTimeout="00:01:00" openTimeout="00:01:00" receiveTimeout="00:10:00" sendTimeout="00:01:00" allowCookies="false" bypassProxyOnLocal="false" hostNameComparisonMode="StrongWildcard" maxBufferSize="65536" maxBufferPoolSize="524288" maxReceivedMessageSize="65536" messageEncoding="Text" textEncoding="utf-8" transferMode="Buffered"
                    useDefaultWebProxy="true">
                    <readerQuotas maxDepth="32" maxStringContentLength="8192" maxArrayLength="16384" maxBytesPerRead="4096" maxNameTableCharCount="16384" />
                    <security mode="None">
                        <transport clientCredentialType="None" proxyCredentialType="None" realm="" />
                        <message clientCredentialType="UserName" algorithmSuite="Default" />
                    </security>
                </binding>		
            </basicHttpBinding>
        </bindings>
        <client>
            <endpoint address="https://tqdttntt.customs.gov.vn/KDTService/service.asmx" binding="basicHttpBinding" bindingConfiguration="ServiceSoap1" contract="ServiceReference2.ServiceSoap" name="ServiceSoap1"/>
            <endpoint address="http://192.168.0.22/KDTService/CISservice.asmx" binding="basicHttpBinding" bindingConfiguration="CISServiceSoap" contract="ServiceReference1.CISServiceSoap" name="CISServiceSoap"/>
            <endpoint address="http://192.168.0.22/KDTService/KDTService.asmx" binding="basicHttpBinding" bindingConfiguration="KDTServiceSoap" contract="ServiceReference3.KDTServiceSoap" name="KDTServiceSoap"/>
            <endpoint address="http://203.210.158.232/TNTTService/Service.asmx" binding="basicHttpBinding" bindingConfiguration="ServiceSoap" contract="ServiceReference4.ServiceSoap" name="ServiceSoap"/>
             <endpoint address="http://10.224.128.113/KDTService/service.asmx" binding="basicHttpBinding" bindingConfiguration="ServiceSoap3" contract="ServiceReference5.ServiceSoap" name="ServiceSoap2" />
        </client>
    </system.serviceModel>
	<runtime>
		<assemblyBinding xmlns="urn:schemas-microsoft-com:asm.v1">
			<probing privatePath="bin5;"/>
			<dependentAssembly>
				<assemblyIdentity name="EnvDTE" publicKeyToken="B03F5F7F11D50A3A" culture="neutral"/>
				<bindingRedirect oldVersion="0.0.0.0-8.0.0.0" newVersion="8.0.0.0"/>
			</dependentAssembly>
		</assemblyBinding>
	</runtime>
    <applicationSettings>
        <TSD.ECUSKDNET.My.MySettings>
            <setting name="ECUS5NET_ECUSService_ECUSService" serializeAs="String">
                <value>http://esign.ecus.net.vn/ECUSService/ECUSService.asmx</value>
            </setting>
            <setting name="ECUS4NET_ECUSService_ECUSService1" serializeAs="String">
                <value>http://etax.net.vn/ECUSService/ECUSService.asmx</value>
            </setting>
            <setting name="ECUS3NET_ECUSService_ECUSService" serializeAs="String">
                <value>http://192.168.0.11/ECUS_WebService/ECUSService.asmx</value>
            </setting>
            <setting name="ECUS5VNACCS_WSHaiQuan4_Service" serializeAs="String">
                <value>http://103.248.160.22/KDTService/Service.asmx</value>
            </setting>
            <setting name="ECUS5VNACCS_WSHaiQuan4TX_CISService" serializeAs="String">
                <value>http://10.224.128.118/KDTServiceAcc/CISService.asmx</value>
            </setting>
           <setting name="ECUS5VNACCS_WSDangKyCKS_CustomService" serializeAs="String">
                <value>http://123.30.23.6/TraLoiDNNoThue/NoThue.asmx</value>
            </setting>	
           <setting name="ECUS5VNACCS_WSKhoCFS_CFSService" serializeAs="String">
                <value>http://localhost:8686/khocfs.asmx</value>
            </setting>
			<setting name="ECUS5VNACCS_TraCuuTTGNT_TraCuuTTGNT" serializeAs="String">
                <value>http://103.248.160.15:8088/TraCuuNopThue/TraCuuTTGNT.asmx</value>
            </setting>
			<setting name="ECUS5VNACCS_DichVuCongFileService_DichVuCongFileService"
                serializeAs="String">
                <value>http://103.248.160.15:8088/SoaDichVuCongFileService/DichVuCongFileService.asmx</value>
            </setting>
            <setting name="ECUS5VNACCS_DichVuCongService_DichVuCongService"
                serializeAs="String">
                <value>http://103.248.160.15:8088/soaDichVuCongService/DichVuCongService.asmx</value>
            </setting>
            <setting name="ECUS5VNACCS_SystemService_SystemService" serializeAs="String">
                <value>http://103.248.160.15:8088/SoaSystemService/SystemService.asmx</value>
            </setting>
            <setting name="ECUS5VNACCS_QRCode_QRCode" serializeAs="String">
                <value>http://localhost:8086/WS_Container/QRCode.asmx</value>
            </setting>
            <setting name="ECUS5VNACCS_MHSService_MHHService" serializeAs="String">
                <value>http://103.248.160.15:8088/TraCuuThongBaoKetQuaPhanLoai/MHSService.asmx</value>
            </setting>
            <setting name="ECUS5VNACCS_TraCuuTTGNT" serializeAs="String">
                <value>http://103.248.160.15:8088/TraCuuNopThue/TraCuuTTGNT.asmx</value>
            </setting>
            <setting name="ECUS5VNACCS_DichVuCongFileService" serializeAs="String">
                <value>http://103.28.37.199/SOADichVuCongFileService/DichVuCongFileService.asmx</value>
            </setting>
            <setting name="ECUS5VNACCS_DichVuCongService" serializeAs="String">
                <value>http://103.28.37.199/SOADichVuCongService/DichVuCongService.asmx</value>
            </setting>
            <setting name="ECUS5VNACCS_SystemService" serializeAs="String">
                <value>http://103.28.37.199/SOASytemService/SystemService.asmx</value>
            </setting>
            <setting name="ECUS5VNACCS_QRCode" serializeAs="String">
                <value>http://103.248.160.25:8086/WS_Container/QRCode.asmx</value>
            </setting>
            <setting name="ECUS5VNACCS_MHHService" serializeAs="String">
                <value>http://103.248.160.15:8088/TraCuuThongBaoKetQuaPhanLoai/MHSService.asmx</value>
            </setting>
			<setting name="ECUS5VNACCS_MobileService" serializeAs="String">
                <value>http://210.245.8.71:92</value>
            </setting>
			<setting name="ECUS5VNACCS_DichVuCongFileServiceCT_TSD" serializeAs="String">
                <value>http://pus.ecus.net.vn/SOADichVuCongFileService/DichVuCongFileService.asmx</value>
            </setting>
            <setting name="ECUS5VNACCS_DichVuCongServiceCT_TSD" serializeAs="String">
                <value>http://pus.ecus.net.vn/SOADichVuCongService/DichVuCongService.asmx</value>
            </setting>
            <setting name="ECUS5VNACCS_SystemServiceCT_TSD" serializeAs="String">
                <value>http://pus.ecus.net.vn/SOASytemService/SystemService.asmx</value>
            </setting>
			
			<setting name="ECUS5VNACCS_DichVuCongFileService_TSD" serializeAs="String">
                <value>http://pus.ecus.net.vn/SUBSOADichVuCongFileService/DichVuCongFileService.asmx</value>
            </setting>
            <setting name="ECUS5VNACCS_DichVuCongService_TSD" serializeAs="String">
                <value>http://pus.ecus.net.vn/SUBSOADichVuCongService/DichVuCongService.asmx</value>
            </setting>
            <setting name="ECUS5VNACCS_SystemService_TSD" serializeAs="String">
                <value>http://pus.ecus.net.vn/SUBSOASytemService/SystemService.asmx</value>
            </setting>
			<setting name="ECUS5VNACCS_SystemServiceHQ_SystemService" serializeAs="String">
                <value>http://pus.ecus.net.vn:8088/SoaSystemServiceCT/SystemService.asmx</value>
            </setting>
			<setting name="ECUS5VNACCS_DichVuCongFileServiceHQ" serializeAs="String">
                <value>http://pus.ecus.net.vn:8088/SoaDichVuCongFileService/DichVuCongFileService.asmx</value>
            </setting>
            <setting name="ECUS5VNACCS_DichVuCongServiceHQ" serializeAs="String">
                <value>http://pus.ecus.net.vn:8088/SoaDichVuCongService/DichVuCongService.asmx</value>
            </setting>
            <setting name="ECUS5VNACCS_SystemServiceHQ" serializeAs="String">
                <value>http://pus.ecus.net.vn:8088/SoaSystemService/SystemService.asmx</value>
            </setting>
			<setting name="ECUS5VNACCS_DichVuCongDanhMuc_DichVuCongDanhMucService" serializeAs="String">
                <value>http://pus.ecus.net.vn:8088/SoaDichVuCongDanhMucCT/DichVuCongDanhMucService.asmx</value>
            </setting>
			<setting name="ECUS5VNACCS_DichVuCongserviceNew_DichVuCongService"
                serializeAs="String">
                <value>http://pus.ecus.net.vn:8088/SoaDichVuCongServiceNewCT/DichVuCongService.asmx</value>
            </setting>
			<setting name="ECUS5VNACCS_DichVuCongFileServiceHQCT" serializeAs="String">
                <value>http://103.248.160.15:8088/SoaDichVuCongFileServiceCT/DichVuCongFileService.asmx</value>
            </setting>
            <setting name="ECUS5VNACCS_DichVuCongServiceHQCT" serializeAs="String">
                <value>http://103.248.160.15:8088/SoaDichVuCongServiceCT/DichVuCongService.asmx</value>
            </setting>
            <setting name="ECUS5VNACCS_SystemServiceHQCT" serializeAs="String">
                <value>http://103.248.160.15:8088/SoaSystemServiceCT/SystemService.asmx</value>
            </setting>
			<setting name="ECUS5VNACCS_DichVuCongServiceHQ_DichVuCongService"
                serializeAs="String">
                <value>http://pus.ecus.net.vn:8088/soaDichVuCongServiceCT/DichVuCongService.asmx</value>
            </setting>
			<setting name="ECUS5VNACCS_DichVuCongFileServiceHQ_DichVuCongFileService"
                serializeAs="String">
                <value>http://pus.ecus.net.vn:8088/SoaDichVuCongFileServiceCT/DichVuCongFileService.asmx</value>
            </setting>
			<setting name="ECUS5VNACCS_HCASLOService_HCAS_LO_Service" serializeAs="String">
				<value>http://101.53.12.67/logistics/HCAS_LO_Service.asmx</value>
		   </setting>
		   <setting name="ECUS5VNACCS_KDTWebserviceDG_KDTService" serializeAs="String">
				<value>http://203.210.158.232:8088/WebServiceDG.asmx</value>
		   </setting>
        </TSD.ECUSKDNET.My.MySettings>
    </applicationSettings>
<startup><supportedRuntime version="v2.0.50727"/></startup>
<system.net>
 <settings>
  <servicePointManager expect100Continue="false" />
 </settings>
</system.net>
</configuration>
