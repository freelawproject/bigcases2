# mypy doesn't like assigning an attribute or function/method to a MagicMock()
#   so those lines have comments so mypy will ignore the [assignment] error.
#   @see  https://github.com/python/mypy/issues/6713
#   Likewise, it does not like return_value or side_effect used with
#   MagicMocks, so those lines are commented to ignore the [attr-defined]
#   error.
import re
from unittest.mock import ANY, MagicMock, call, patch

from django.test import SimpleTestCase

from bc.core.management.commands.make_dev_data import MakeDevData
from bc.subscription.tests.factories import SubscriptionFactory

CL_DOCKET_RESULT = {
    "docket_id": 42,
    "docket_number": "US 12345",
    "case_name": "US v Bobolink",
    "court_id": 5,
    "pacer_case_id": 89,
    "slug": "cl_slug_for_docket",
}


class TestMakeDataDev(SimpleTestCase):
    def test_default_values(self) -> None:
        maker = MakeDevData()

        self.assertEqual(1, maker.num_big_case_subscriptions)
        self.assertEqual(1, maker.num_little_case_subscriptions)
        self.assertEqual([], maker.subscribed_dockets)


@patch.object(MakeDevData, "make_admin_users", return_value="admin")
@patch.object(MakeDevData, "make_big_cases_group_and_channels")
@patch.object(MakeDevData, "make_little_cases_group_and_channels")
@patch.object(
    MakeDevData, "make_subscriptions", return_value=([], "made subs")
)
@patch.object(
    MakeDevData,
    "subscribe_randoms_to_group",
    return_value=([], "subbed randoms"),
)
class TestCreate(SimpleTestCase):
    cl_docket_result: dict[str, object] = {}
    mock_big_cases_group: MagicMock = MagicMock()
    mocked_make_big_cases_group_and_channels: MagicMock = MagicMock()
    mocked_make_little_cases_group_and_channels: MagicMock = MagicMock()

    @classmethod
    def setUpClass(cls) -> None:
        cls.cl_docket_result = CL_DOCKET_RESULT

        mocked_big_cases_group = MagicMock()
        mocked_big_cases_group.channels = ["ch1", "ch2"]
        cls.mock_big_cases_group = mocked_big_cases_group

        mocked_make_big_cases_group_and_channels = MagicMock()
        mocked_make_big_cases_group_and_channels.return_value = (
            mocked_big_cases_group,
            "made big_cases group",
        )
        cls.mocked_make_big_cases_group_and_channels = (
            mocked_make_big_cases_group_and_channels
        )

        mocked_make_little_cases_group_and_channels = MagicMock()
        mocked_make_little_cases_group_and_channels.return_value = (
            mocked_big_cases_group,
            "made little_cases group",
        )
        cls.mocked_make_little_cases_group_and_channels = (
            mocked_make_little_cases_group_and_channels
        )

    def _mock_maker_groups_methods(self, maker: MakeDevData) -> None:
        """
        Helper method for testing that refactors out commonly needed mocking
        """
        maker.big_cases_group = self.mock_big_cases_group  # type: ignore[assignment]
        maker.make_big_cases_group_and_channels = (  # type: ignore[assignment]
            self.mocked_make_big_cases_group_and_channels
        )  # type: ignore[assignment]

        # Turn off the IntelliJ IDE formatter so it doesn't wrap the
        # type...  comment
        # @formatter:off
        maker.make_little_cases_group_and_channels = (  # type: ignore[assignment]
            self.mocked_make_little_cases_group_and_channels
        )  # type: ignore[assignment]
        # @formatter:on

    def test_makes_1_admin(
        self,
        _mock_subscribe_randoms_to_group,
        _mock_make_subscriptions,
        _mock_make_little_cases_group_and_channels,
        _mock_make_big_cases_group_and_channels,
        mock_admin_users,
    ) -> None:
        maker = MakeDevData()
        self._mock_maker_groups_methods(maker)
        maker.create()

        mock_admin_users.assert_called_with()

    def test_makes_1_big_cases_group_and_channels(
        self,
        _mock_subscribe_randoms_to_group,
        _mock_make_subscriptions,
        _mock_make_little_cases_group_and_channels,
        _mock_make_big_cases_group_and_channels,
        _mock_admin_users,
    ) -> None:
        maker = MakeDevData(10, 10)
        self._mock_maker_groups_methods(maker)
        maker.create()

        self.mocked_make_big_cases_group_and_channels.assert_called_with()

    def test_makes_1_little_cases_group_and_channels(
        self,
        _mock_subscribe_randoms_to_group,
        _mock_make_subscriptions,
        _mock_make_little_cases_group_and_channels,
        _mock_make_big_cases_group_and_channels,
        _mock_admin_users,
    ) -> None:
        maker = MakeDevData(10, 10)
        self._mock_maker_groups_methods(maker)
        maker.create()

        self.mocked_make_little_cases_group_and_channels.assert_called_with()

    def test_no_big_cases_makes_only_little(
        self,
        mock_subscribe_randoms_to_group,
        _mock_make_subscriptions,
        _mock_make_little_cases_group_and_channels,
        _mock_make_big_cases_group_and_channels,
        _mock_admin_users,
    ) -> None:
        maker = MakeDevData(0, 1)
        self._mock_maker_groups_methods(maker)
        maker.create()

        expected_sub_randoms_calls = [call(ANY, 1, ANY)]
        self.assertEqual(
            expected_sub_randoms_calls,
            mock_subscribe_randoms_to_group.call_args_list,
        )

    def test_only_big_cases_makes_no_little(
        self,
        mock_subscribe_randoms_to_group,
        _mock_make_subscriptions,
        _mock_make_little_cases_group_and_channels,
        _mock_make_big_cases_group_and_channels,
        _mock_admin_users,
    ) -> None:
        maker = MakeDevData(3, 0)
        self._mock_maker_groups_methods(maker)
        maker.make_subscriptions.return_value = (  # type: ignore[attr-defined]
            ["one", "two", "three", "four"],
            "made subs",
        )
        maker.create()

        expected_sub_randoms_calls = [
            call(
                self.mock_big_cases_group, 3, ["one", "two", "three", "four"]
            ),
        ]
        self.assertEqual(
            expected_sub_randoms_calls,
            mock_subscribe_randoms_to_group.call_args_list,
        )

    def test_no_little_cases_makes_only_big(
        self,
        mock_subscribe_randoms_to_group,
        _mock_make_subscriptions,
        _mock_make_little_cases_group_and_channels,
        _mock_make_big_cases_group_and_channels,
        _mock_admin_users,
    ) -> None:
        maker = MakeDevData(1, 0)
        self._mock_maker_groups_methods(maker)
        maker.create()

        expected_sub_randoms_calls = [
            call(self.mock_big_cases_group, 1, []),
        ]
        self.assertEqual(
            expected_sub_randoms_calls,
            mock_subscribe_randoms_to_group.call_args_list,
        )

    def test_only_little_cases_makes_only_little(
        self,
        mock_subscribe_randoms_to_group,
        _mock_make_subscriptions,
        _mock_make_little_cases_group_and_channels,
        _mock_make_big_cases_group_and_channels,
        _mock_admin_users,
    ) -> None:
        maker = MakeDevData(0, 1)
        self._mock_maker_groups_methods(maker)
        maker.make_subscriptions.return_value = (  # type: ignore[attr-defined]
            ["one", "two", "three", "four"],
            "made subs",
        )
        maker.create()

        self.mocked_make_big_cases_group_and_channels.assert_called_with()
        expected_sub_randoms_calls = [
            call(ANY, 1, ["one", "two", "three", "four"])
        ]
        self.assertEqual(
            expected_sub_randoms_calls,
            mock_subscribe_randoms_to_group.call_args_list,
        )

    def test_big_and_little_cases_makes_big_and_little(
        self,
        mock_subscribe_randoms_to_group,
        _mock_make_subscriptions,
        _mock_make_little_cases_group_and_channels,
        _mock_make_big_cases_group_and_channels,
        _mock_admin_users,
    ) -> None:
        maker = MakeDevData(2, 1)
        self._mock_maker_groups_methods(maker)
        maker.make_subscriptions.return_value = (  # type: ignore[attr-defined]
            ["one", "two", "three"],
            "made subs",
        )  # type: ignore[attr-defined]

        # Set the return values for each call
        # Turn off the IntelliJ IDE formatter so it doesn't wrap the
        # type...  comment
        # @formatter:off
        maker.subscribe_randoms_to_group.side_effect = [  # type: ignore[attr-defined]
            (["one", "three"], "subbed big cases"),
            (["two"], "subbed little cases"),
        ]  # type: ignore[attr-defined]
        # @formatter:on
        maker.create()

        self.mocked_make_big_cases_group_and_channels.assert_called_with()
        expected_sub_randoms_calls = [
            call(self.mock_big_cases_group, 2, ["one", "two", "three"]),
            call(ANY, 1, ["two"]),
        ]
        self.assertEqual(
            expected_sub_randoms_calls,
            mock_subscribe_randoms_to_group.call_args_list,
        )

    def test_makes_subscriptions(
        self,
        _mock_subscribe_randoms_to_group,
        mock_make_subscriptions,
        _mock_make_little_cases_group_and_channels,
        _mock_make_big_cases_group_and_channels,
        _mock_admin_users,
    ) -> None:
        maker = MakeDevData(2, 3, [1234])
        self._mock_maker_groups_methods(maker)
        maker.create()

        mock_make_subscriptions.assert_called_with(5, [1234])

    def test_returns_made_strs_with_linefeeds(
        self,
        _mock_subscribe_randoms_to_group,
        _mock_make_subscriptions,
        _mock_make_little_cases_group_and_channels,
        _mock_make_big_cases_group_and_channels,
        _mock_admin_users,
    ) -> None:
        maker = MakeDevData(10, 10, None)
        self._mock_maker_groups_methods(maker)
        result = maker.create()

        expected = (
            "\nCreated and saved data. Made:\n"
            "admin\n"
            "made big_cases group\n"
            "made little_cases group\n"
            "made subs\n"
            f"{maker.INDENT_STR}subbed randoms\n"
            f"{maker.INDENT_STR}subbed randoms\n"
        )
        self.assertEqual(expected, result)


class TestMakeSubscriptions(SimpleTestCase):
    def test_default_values(self) -> None:
        mock_make_random_subs = MagicMock()
        mock_make_random_subs.return_value = [], "Made random subs"

        maker = MakeDevData()
        maker.make_subs_from_cl_docket_ids = MagicMock()  # type: ignore[assignment]
        maker.make_random_subscriptions = mock_make_random_subs  # type: ignore[assignment]

        maker.make_subscriptions()

        # maker.DEFAULT_NUM_BIG_CASES + maker.DEFAULT_NUM_LITTLE_CASES = 1 + 1
        expected_num_random = 2
        mock_make_random_subs.assert_called_with(expected_num_random)
        maker.make_subs_from_cl_docket_ids.assert_not_called()

    def test_no_cl_docket_ids(self) -> None:
        maker = MakeDevData()
        maker.make_subs_from_cl_docket_ids = MagicMock()  # type: ignore[assignment]

        maker.make_subscriptions(0, [])

        maker.make_subs_from_cl_docket_ids.assert_not_called()

    def test_only_cl_docket_ids(self) -> None:
        mock_make_subs_from_cl_docket_id = MagicMock()
        mock_make_subs_from_cl_docket_id.return_value = [], "Made docket subs"

        maker = MakeDevData()
        maker.make_subs_from_cl_docket_ids = mock_make_subs_from_cl_docket_id  # type: ignore[assignment]
        maker.make_random_subscriptions = MagicMock()  # type: ignore[assignment]

        maker.make_subscriptions(0, [1234, 5678])
        mock_make_subs_from_cl_docket_id.assert_called_with([1234, 5678])
        maker.make_random_subscriptions.assert_not_called()

    def test_no_random_subs(self) -> None:
        maker = MakeDevData()
        maker.make_random_subscriptions = MagicMock()  # type: ignore[assignment]

        maker.make_subscriptions(0)

        maker.make_random_subscriptions.assert_not_called()

    def test_only_random_subs(self) -> None:
        mock_make_random_subs = MagicMock()
        mock_make_random_subs.return_value = [], "Made random subs"

        maker = MakeDevData()
        maker.make_subs_from_cl_docket_ids = MagicMock()  # type: ignore[assignment]
        maker.make_random_subscriptions = mock_make_random_subs  # type: ignore[assignment]

        maker.make_subscriptions(2)

        maker.make_random_subscriptions.assert_called_with(2)
        maker.make_subs_from_cl_docket_ids.assert_not_called()

    def test_both_randoms_and_cl_dockets_made(self) -> None:
        mock_make_subs_from_cl_docket_id = MagicMock()
        mock_make_subs_from_cl_docket_id.return_value = [], "Made docket subs"

        mock_make_random_subs = MagicMock()
        mock_make_random_subs.return_value = [], "Made random subs"

        maker = MakeDevData()
        maker.make_subs_from_cl_docket_ids = mock_make_subs_from_cl_docket_id  # type: ignore[assignment]
        maker.make_random_subscriptions = mock_make_random_subs  # type: ignore[assignment]

        maker.make_subscriptions(2, [1234, 5678])

        maker.make_random_subscriptions.assert_called_with(2)
        maker.make_subs_from_cl_docket_ids.assert_called_with([1234, 5678])

    def test_result_str_is_concat_with_linefeed(self) -> None:
        mock_make_subs_from_cl_docket_id = MagicMock()
        mock_make_subs_from_cl_docket_id.return_value = [], "docket string"
        mock_make_random_subs = MagicMock()
        mock_make_random_subs.return_value = [], "random string"

        maker = MakeDevData()
        maker.make_subs_from_cl_docket_ids = mock_make_subs_from_cl_docket_id  # type: ignore[assignment]
        maker.make_random_subscriptions = mock_make_random_subs  # type: ignore[assignment]

        _, subs_str = maker.make_subscriptions(3, [1234, 5678])
        self.assertEqual("docket string\nrandom string", subs_str)


class NumSubdToGroupStrTest(SimpleTestCase):
    """
    Mixin to test a string matches a 'subscribed to group...'
    str
    """

    def has_group_subscribed_str(
        self, num: int = 0, group_str: str = "", actual_str=""
    ):
        expected_indented_subcribed = f"  {num} subscribed to {group_str}"
        self.assertRegex(actual_str, re.compile(expected_indented_subcribed))


# Note that we're mocking the function that has already been
# imported by make_dev_data so it must be specified as within
# ...make_dev_data...
# @see https://docs.python.org/3/library/unittest.mock.html#where-to-patch
@patch("bc.core.management.commands.make_dev_data.lookup_docket_by_cl_id")
class TestMakeSubsFromClDocketId(NumSubdToGroupStrTest, SimpleTestCase):
    cl_docket_result: dict[str, object] = {}
    mocked_channels: MagicMock = MagicMock()
    mock_big_cases_group: MagicMock = MagicMock()

    @classmethod
    def setUpClass(cls) -> None:
        cls.cl_docket_result = CL_DOCKET_RESULT
        # Mock channels so that it can receive .all() and .list()
        mocked_channels = MagicMock()
        mocked_channels.all.return_value = mocked_channels.list()
        mocked_channels.list.return_value = ["ch1", "ch2"]
        cls.mocked_channels = mocked_channels
        mocked_big_cases_group = MagicMock()
        mocked_big_cases_group.channels = mocked_channels
        cls.mock_big_cases_group = mocked_big_cases_group

    @patch.object(SubscriptionFactory, "create")
    def test_looks_up_cl_docket_id(
        self, _mock_sub_factory_create, mock_cl_lookup_docket_by_cl_id
    ) -> None:
        mock_cl_lookup_docket_by_cl_id.return_value = self.cl_docket_result
        maker = MakeDevData()
        maker.big_cases_group = self.mock_big_cases_group  # type: ignore[assignment]
        maker.make_subs_from_cl_docket_ids([12345, 67890])

        expected_calls = [call(12345), call(67890)]
        self.assertEqual(
            expected_calls, mock_cl_lookup_docket_by_cl_id.call_args_list
        )

    @patch.object(SubscriptionFactory, "create")
    def test_creates_subs_from_factory(
        self, mock_sub_factory_create, mock_cl_lookup_docket_by_cl_id
    ) -> None:
        mock_cl_lookup_docket_by_cl_id.return_value = self.cl_docket_result
        maker = MakeDevData()
        maker.big_cases_group = self.mock_big_cases_group  # type: ignore[assignment]
        maker.make_subs_from_cl_docket_ids([12345, 67890])

        mock_sub_factory_create.assert_called_with(
            cl_docket_id=67890,
            docket_number="US 12345",
            docket_name="US v Bobolink",
            cl_court_id=5,
            pacer_case_id=89,
            cl_slug="cl_slug_for_docket",
            channels=self.mock_big_cases_group.channels.all(),
        )

    @patch.object(SubscriptionFactory, "create")
    def test_returns_made_str(
        self,
        _mock_sub_factory_create,
        mock_cl_lookup_docket_by_cl_id,
    ) -> None:
        # calls made_str to return results info
        mock_cl_lookup_docket_by_cl_id.return_value = self.cl_docket_result
        maker = MakeDevData()
        maker.big_cases_group = self.mock_big_cases_group  # type: ignore[assignment]
        _, made_str = maker.make_subs_from_cl_docket_ids([1, 2, 3])

        self.assertRegex(
            made_str,
            r"3 Real subscription\(s\) (.)+ docket ids \[1, 2, 3\]",
        )
        self.has_group_subscribed_str(3, f"{maker.big_cases_group}", made_str)


class TestMakeRandomSubscriptions(SimpleTestCase):
    @patch.object(SubscriptionFactory, "create")
    def test_calls_sub_factory_num_times(
        self, mock_sub_factory_create
    ) -> None:
        MakeDevData().make_random_subscriptions(3)
        self.assertEqual(3, mock_sub_factory_create.call_count)

    @patch.object(SubscriptionFactory, "create")
    def test_returns_made_str(self, _mock_sub_factory_create) -> None:
        # calls made_str to return results info
        _, result_str = MakeDevData().make_random_subscriptions(3)

        self.assertRegex(result_str, r"\d+ Subscriptions \(random\)")


class TestSubscribeRandomToGroup(NumSubdToGroupStrTest, SimpleTestCase):
    mock_group: MagicMock = MagicMock()

    @classmethod
    def setUpClass(cls) -> None:
        mocked_group = MagicMock()
        mocked_group.channels.all.return_value = ["ch 1"]
        cls.mock_group = mocked_group

    def test_no_subs_given_returns_empty_list(self) -> None:
        subs, _ = MakeDevData().subscribe_randoms_to_group(self.mock_group, 1)

        self.assertEqual([], subs)

    def test_num_is_zero_returns_empty_list(self) -> None:
        subs, _ = MakeDevData().subscribe_randoms_to_group(
            self.mock_group, 0, [MagicMock()]
        )

        self.assertEqual([], subs)

    def test_num_are_subscribed(self) -> None:
        mock_sub_1 = MagicMock(return_value=[])
        mock_sub_2 = MagicMock(return_value=[])
        mock_sub_3 = MagicMock(return_value=[])

        subbed, _ = MakeDevData().subscribe_randoms_to_group(
            self.mock_group, 2, [mock_sub_1, mock_sub_2, mock_sub_3]
        )

        self.assertEqual(2, len(subbed))

    def test_subscribed_to_channels(self) -> None:
        mock_sub_1 = MagicMock()
        mock_sub_1.channel.return_value = []

        MakeDevData().subscribe_randoms_to_group(
            self.mock_group, 1, [mock_sub_1]
        )

        mock_sub_1.channel.add.assert_called_with("ch 1")

    def test_returns_list_subbed(self) -> None:
        mock_sub_1 = MagicMock()
        mock_sub_1.channel.return_value = []
        mock_sub_2 = MagicMock()
        mock_sub_2.channel.return_value = []

        (
            subs_added_to_group,
            _,
        ) = MakeDevData().subscribe_randoms_to_group(
            self.mock_group, 2, [mock_sub_1, mock_sub_2]
        )

        self.assertEqual(2, len(subs_added_to_group))
        self.assertIn(mock_sub_1, subs_added_to_group)
        self.assertIn(mock_sub_2, subs_added_to_group)

    def test_returns_subs_str(self) -> None:
        mock_sub_1 = MagicMock()
        mock_sub_1.channel.return_value = []
        mock_sub_2 = MagicMock()
        mock_sub_2.channel.return_value = []

        (
            _,
            subbed_str,
        ) = MakeDevData().subscribe_randoms_to_group(
            self.mock_group, 2, [mock_sub_1, mock_sub_2]
        )
        self.has_group_subscribed_str(2, f"{self.mock_group}", subbed_str)
