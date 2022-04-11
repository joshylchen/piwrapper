
import datetime
import json
import requests
import urllib3
import pandas as pd
from dataclasses import dataclass
from requests_kerberos import HTTPKerberosAuth, OPTIONAL, REQUIRED
from typing import Any, Dict, List, Optional, Tuple
from piwrapper.PiConsts import BufferOption, RetrievalMode, UpdateOption


@dataclass
class PIValue:
    """
    Represents a single PI value
    #two ways to pass timestamp
    1 datetime.datetime(2021,11,13,21,00)
    2 import dateutil
    dateutil.parser.parse("2021-11-13T21:00:00")
    """

    time_stamp: datetime.datetime = datetime.datetime.min
    units_abbreviation: Optional[str] = None
    good: Optional[bool] = None
    questionable: Optional[bool] = None
    value: Optional[Any] = None

    def to_json(self) -> str:
        """
        Serialize to a json string
        :return: json representation of the object
        """
        tmp_dict = {"Timestamp": self.time_stamp.isoformat()}
        if self.units_abbreviation is not None:
            tmp_dict["UnitsAbbreviation"] = self.units_abbreviation
        if self.good is not None:
            tmp_dict["Good"] = self.good
        if self.questionable is not None:
            tmp_dict["Questionable"] = self.questionable
        if self.value is not None:
            tmp_dict["Value"] = self.value
        return json.dumps(obj=tmp_dict)

class Connection:
    """
    Pi class for connecting to the PI REST API
    """

    def __init__(
        self,
        server: str,
        basic_credentials: Optional[Tuple[str, str]] = None,
        verify: bool = True,
    ):
        """
        Initialises connection instance

        :param basic_credentials: Optional tuple of username password strings if basic authentication is used
        :param server: URI for the PI REST API server
        :verify: Verify the certificate of the server before connecting
        """

        if basic_credentials is None:
            self.auth = HTTPKerberosAuth(
                mutual_authentication=REQUIRED if verify else OPTIONAL
            )
        else:
            self.auth = basic_credentials

        self.base_url: str = server
        self.starting_url: str = f"""https://{self.base_url}/piwebapi/"""
        self.verify: bool = verify


        if self.verify is False:
            # Disable the insecure request warnings if the user doesn't want to check URL certificates
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def get_data_servers(self) -> list:
        """
        Get all dataservers
        :return: list of data servers
        raise: connectionError: fail to connect to Pi server
        """
        response: requests.Response = requests.get(
            self.starting_url,
            auth=self.auth,
            headers={"Content-Type": "application/json"},
            verify=self.verify,
        )

        if response.status_code != requests.codes.ok:
            raise ConnectionError("Connection to PI REST API Server failed")

        top_level_content = json.loads(s=response.content)

        # Get data server
        data_servers_url = top_level_content["Links"]["DataServers"]
        data_server_response: requests.Response = requests.get(
            data_servers_url,
            auth=self.auth,
            headers={"Content-Type": "application/json"},
            verify=self.verify,
        )
        data_server_content_list = json.loads(s=data_server_response.content)
        self.data_server_list: List[Dict[str, Any]] = [
            data_server_content
            for data_server_content in data_server_content_list["Items"]
        ]
        return self.data_server_list
    def _find_pi_webid(
        self,
        pi_tag: str) ->dict:
        """
        Search associated webid for pi_tag
        :param: pi_tag: full or partial pi tag name
        :return: dictionary with tag name as key and webid as value
        :raise LookupError: No matching tag can be found
        :raise ValueError: No valid response returned
        """
        pi_tag_url: str = f"""{self.starting_url}search/query?q=name:{pi_tag}"""
        response: requests.Response = requests.get(
            pi_tag_url,
            auth=self.auth,
            headers={"Content-Type": "application/json"},
            verify=self.verify,
        )
        if response.status_code != requests.codes.ok:
            raise LookupError(response)
        response_dict : Dict[str, Any] =json.loads(s=response.content)
        if response_dict["Items"]:
            webid_dic = {idx["Name"]: idx["WebId"] for idx in response_dict["Items"] }
        else:
            raise ValueError("No response. Please check tag name")

        return webid_dic
    def _single_interpolated_value_getter(
        self,
        webid: str):
        """
        get interpolated value in data frame for single webid
        :param webid: webid
        :return: interpolated value in a dataframe
        :raise LookupError: No matching tag can be found
        :raise ValueError: No response with the webid.
       """        
        resource_url: str = f"""{self.starting_url}streams/{webid}/interpolated"""
        response: requests.Response = requests.get(
            resource_url,
            auth=self.auth,
            headers={"Content-Type": "application/json"},
            verify=self.verify,
        )

        if response.status_code != requests.codes.ok:
            raise LookupError(response)
        response_dict : Dict[str, Any] =json.loads(s=response.content)
        if response_dict["Items"]:
            response_df = pd.DataFrame(response_dict["Items"])
        else:
            raise ValueError("No response. Please check webid")
        return response_df

    def get_interpolated_value(   
        self,
        pi_tag: str):
        """
        get pi point interpolated value
        :param pi_tag: name of pi tag
        :return: interpolated value in a dataframe
        :raise LookupError: No matching tag can be found
        :raise ValueError: more than one tags foud
        """
        webid_dic: Dict[str, Any]  = self._find_pi_webid(pi_tag)
        if len(webid_dic) > 1:
            raise ValueError(f"more than one tags have been found: {webid_dic.keys()}, use get_interpolated_values method instead")
        _, v = next(iter(webid_dic.items()))
        response_df=self._single_interpolated_value_getter(v)
        return response_df

    def get_interpolated_values(   
        self,
        pi_tag: str) -> dict:
        """
        get pi point interpolated value
        :param pi_tag: name of pi tag
        :return: nested interpolated value in the DICTIONARY 
        with tag name as key as interpolated value as value
        :raise LookupError: No matching tag can be found
        """
        webid_dic: Dict[str, Any]  = self._find_pi_webid(pi_tag)
        tag_names = list(webid_dic.keys())
        response_dict : Dict[str, Any] = {tag: self._single_interpolated_value_getter(webid_dic[tag]) for tag in tag_names }

        return response_dict
    def update_value(
        self,
        value: PIValue,
        update_option: UpdateOption,
        buffer_option: BufferOption,
        pi_tag: str = None,
        webid: str = None
    ) -> str:
        """
        Update a value for the specified pi tag

        :param value: value to update with Dataclass attributes
        :param pi_tag: update the value for this pi_tag
        :param update_option: update mode to apply
        :param buffer_option: buffering more to apply
        :param web_id: use web_id to update 
        :return: Location or the added object if successful
        :raises ValueError: cannot have both webid and pi_tag at the same time
        :raises ValueError: cannot have more than one webid
        :raises LookupError: Failed to post an update to the current web_id
        """

        if webid is not None and pi_tag is not None:
            raise ValueError("Cannot pass both webid and pi_tag at the same time")
        if webid == None:
            webid_dic: Dict[str, Any]  = self._find_pi_webid(pi_tag)
            if len(webid_dic) > 1:
                raise ValueError(f"more than one associated webids have been found: {webid_dic.keys()}, use single webid instead")
            _, v = next(iter(webid_dic.items()))
            url: str = (f"{self.starting_url}streams/{v}/value?updateOption={update_option.value}&bufferOption={buffer_option.value}")
        else:
            url: str = (f"{self.starting_url}streams/{webid}/value?updateOption={update_option.value}&bufferOption={buffer_option.value}")        
        response: requests.Response = requests.post(
            url=url,
            data=value.to_json(),
            auth=self.auth,
            headers={"Content-Type": "application/json"},
            verify=self.verify,
        )


        if response.status_code != requests.codes.ok and response.status_code != requests.codes.no_content:
            raise LookupError(response)

        return response.headers["Location"]


    def _single_recordedattime_value_getter(
        self,
        webid: str,
        time:str,
        retrival_mode: RetrievalMode    
        ):
        """
        get recorded value in data frame for single webid
        :param webid: webid
        :param retrival_mode: how to retrive the recorded value
        :param time: specific time or relative time
        :return: single recorded value
        :raise LookupError: No matching tag can be found
        :raise ValueError: No response with the webid.
       """        
        resource_url: str = f"""{self.starting_url}streams/{webid}/recordedattime?retrievalMode={retrival_mode.value}&time={time}"""
        response: requests.Response = requests.get(
            resource_url,
            auth=self.auth,
            headers={"Content-Type": "application/json"},
            verify=self.verify,
        )

        if response.status_code != requests.codes.ok:
            raise LookupError(response)
        response_dict : Dict[str, Any] =json.loads(s=response.content)
        if response_dict["Value"]:
            if retrival_mode.value == "Exact":
                response = response_dict["Value"]["Value"]
            else:
                response = response_dict["Value"]
        else:
            raise ValueError("No response. Please check webid")
        return response

    def get_recordedattime_value(   
        self,
        pi_tag: str,
        time:str,
        retrival_mode: RetrievalMode      
        ):
        """
        get pi point recorded value
        :param pi_tag: name of pi tag
        :param retrival_mode: how to retrive the recorded value
        :param time: specific time or relative time        
        :return: single recorded value
        :raise LookupError: No matching tag can be found
        :raise ValueError: more than one tags foud
        """
        webid_dic: Dict[str, Any]  = self._find_pi_webid(pi_tag)
        if len(webid_dic) > 1:
            raise ValueError(f"more than one tags have been found: {webid_dic.keys()}, use get_interpolated_values method instead")
        _, v = next(iter(webid_dic.items()))
        response=self._single_recordedattime_value_getter(v,time,retrival_mode)
        return response

    def get_recordedattim_values(   
        self,
        pi_tag: str,
        time:str,
        retrival_mode: RetrievalMode) -> dict:
        """
        get pi point interpolated value
        :param pi_tag: name of pi tag
        :param retrival_mode: how to retrive the recorded value
        :param time: specific time or relative time   
        :return: nested interpolated value in the DICTIONARY 
        with tag name as key as interpolated value as value
        :raise LookupError: No matching tag can be found
        """
        webid_dic: Dict[str, Any]  = self._find_pi_webid(pi_tag)
        tag_names = list(webid_dic.keys())
        response_dict : Dict[str, Any] = {tag: self._single_recordedattime_value_getter(webid_dic[tag],time,retrival_mode) for tag in tag_names }

        return response_dict



