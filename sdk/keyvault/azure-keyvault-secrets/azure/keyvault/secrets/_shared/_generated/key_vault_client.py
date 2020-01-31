# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.profiles import KnownProfiles, ProfileDefinition
from azure.profiles.multiapiclient import MultiApiClientMixin

from .v7_0.version import VERSION as V7_0_VERSION
from .v2016_10_01.version import VERSION as V2016_10_01_VERSION


class KeyVaultClient(MultiApiClientMixin):
    """The key vault client performs cryptographic key operations and vault operations against the Key Vault service.
    Implementation depends on the API version:

         * 2016-10-01: :class:`v2016_10_01.KeyVaultClient<azure.keyvault._generated.v2016_10_01.KeyVaultClient>`
         * 7.0: :class:`v7_0.KeyVaultClient<azure.keyvault._generated.v7_0.KeyVaultClient>`

    :param credentials: Credentials needed for the client to connect to Azure.
    :type credentials: :mod:`A msrestazure Credentials
     object<msrestazure.azure_active_directory>`

    :param str api_version: API version to use if no profile is provided, or if
     missing in profile.
    :param profile: A profile definition, from KnownProfiles to dict.
    :type profile: azure.profiles.KnownProfiles
    """

    DEFAULT_API_VERSION = V7_0_VERSION
    _PROFILE_TAG = "azure.keyvault.KeyVaultClient"
    LATEST_PROFILE = ProfileDefinition({_PROFILE_TAG: {None: DEFAULT_API_VERSION}}, _PROFILE_TAG + " latest")

    _init_complete = False

    def __init__(self, credentials, pipeline=None, api_version=None, profile=KnownProfiles.default):
        self._pipeline = pipeline
        self._entered = False
        super(KeyVaultClient, self).__init__(api_version=api_version, profile=profile)

        self._credentials = credentials

        # create client
        api_version = self._get_api_version(None)
        if api_version == V7_0_VERSION:
            from .v7_0 import KeyVaultClient as ImplClient
        elif api_version == V2016_10_01_VERSION:
            from .v2016_10_01 import KeyVaultClient as ImplClient
        else:
            raise NotImplementedError("API version {} is not available".format(api_version))
        self._client = ImplClient(credentials=self._credentials, pipeline=self._pipeline)
        self._init_complete = True

    @staticmethod
    def get_configuration_class(api_version, aio=False):
        """
        Get the versioned configuration implementation corresponding to the current profile.
        :return: The versioned configuration implementation.
        """
        if api_version == V7_0_VERSION:
            from .v7_0._configuration import KeyVaultClientConfiguration as ImplConfig
        elif api_version == V2016_10_01_VERSION:
            from .v2016_10_01._configuration import KeyVaultClientConfiguration as ImplConfig
        else:
            raise NotImplementedError("API version {} is not available".format(api_version))
        return ImplConfig

    @property
    def models(self):
        """Module depends on the API version:
            * 2016-10-01: :mod:`v2016_10_01.models<azure.keyvault._generated.v2016_10_01.models>`
            * 7.0: :mod:`v7_0.models<azure.keyvault._generated.v7_0.models>`
        """
        api_version = self._get_api_version(None)

        if api_version == V7_0_VERSION:
            from .v7_0 import models as impl_models
        elif api_version == V2016_10_01_VERSION:
            from .v2016_10_01 import models as impl_models
        else:
            raise NotImplementedError("APIVersion {} is not available".format(api_version))
        return impl_models

    def __enter__(self, *args, **kwargs):
        """
        Calls __enter__ on all client implementations which support it
        :param args: positional arguments to relay to client implementations of __enter__
        :param kwargs: keyword arguments to relay to client implementations of __enter__
        :return: returns the current KeyVaultClient instance
        """
        self._client.__enter__(*args, **kwargs)
        return self

    def __exit__(self, *args, **kwargs):
        """
        Calls __exit__ on all client implementations which support it
        :param args: positional arguments to relay to client implementations of __enter__
        :param kwargs: keyword arguments to relay to client implementations of __enter__
        :return: returns the current KeyVaultClient instance
        """
        self._client.__exit__(*args, **kwargs)
        return self

    def __getattr__(self, name):
        """
        In the case that the attribute is not defined on the custom KeyVaultClient.  Attempt to get
        the attribute from the versioned client implementation corresponding to the current profile.
        :param name: Name of the attribute retrieve from the current versioned client implementation
        :return: The value of the specified attribute on the current client implementation.
        """
        return getattr(self._client, name)

    def __setattr__(self, name, attr):
        """
        Sets the specified attribute either on the custom KeyVaultClient or the current underlying implementation.
        :param name: Name of the attribute to set
        :param attr: Value of the attribute to set
        :return: None
        """
        if self._init_complete and not hasattr(self, name):
            setattr(self._client, name, attr)
        else:
            super(KeyVaultClient, self).__setattr__(name, attr)
