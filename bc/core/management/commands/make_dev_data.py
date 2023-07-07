# This is based on CourtListener cl/lib/management/make_dev_data.py

from faker import Faker

from bc.channel.models import Group
from bc.channel.tests.factories import ChannelFactory, GroupFactory
from bc.subscription.models import Subscription
from bc.subscription.tests.factories import SubscriptionFactory
from bc.subscription.utils.courtlistener import lookup_docket_by_cl_id
from bc.users.tests.factories import AdminFactory

fake = Faker()


class MakeDevData:
    """
    Creates data using factories.

    The create method actually creates the data (and returns a string with
    a summary of what was created).
    Ex:
      maker = MakeDevData(2, 1, [1234])
      result_str = maker.create()
    """

    NUM_ADMIN_USERS = 1
    NUM_BIGCASES_GROUPS = 1
    NUM_LITTLECASES_GROUPS = 1

    DEFAULT_NUM_BIG_CASES = 1
    DEFAULT_NUM_LITTLE_CASES = 1

    num_big_case_subscriptions = DEFAULT_NUM_BIG_CASES
    num_little_case_subscriptions = DEFAULT_NUM_LITTLE_CASES
    docket_ids: list[int] = []
    big_cases_group: Group | None

    def __init__(
        self,
        num_big_cases: int = DEFAULT_NUM_BIG_CASES,
        num_little_cases: int = DEFAULT_NUM_LITTLE_CASES,
        docket_ids: list[int] | None = None,
    ) -> None:
        self.big_cases_group = None
        self.num_big_case_subscriptions = num_big_cases
        self.num_little_case_subscriptions = num_little_cases
        if docket_ids is None:
            self.subscribed_dockets = []
        else:
            self.subscribed_dockets = docket_ids

    def create(self) -> str:
        """
        Create the objects needed:
          1 Admin user
          1 Group for big cases, with 2 associated channels
          1 Group for little cases, with 2 associated channels
          Subscriptions:
            - creates (number of big cases given + number of little cases
            given) subscriptions with randomly generated info
            - If any docket ids are given:
                - gets docket info from CourtListener and creates
                  subscriptions based on those.
                - subscribes these to the big cases group

        :return: a human-readable string showing what was created
        :rtype: str
        """
        result_str = "\nCreated and saved data. Made:\n"

        result_str += f"{self.make_admin_users()}\n"

        (
            self.big_cases_group,
            big_cases_made_str,
        ) = self.make_big_cases_group_and_channels()
        result_str += f"{big_cases_made_str}\n"

        (
            little_cases_group,
            little_cases_made_str,
        ) = self.make_little_cases_group_and_channels()
        result_str += f"{little_cases_made_str}\n"

        all_subscriptions, subs_made_str = self.make_subscriptions(
            self.num_big_case_subscriptions
            + self.num_little_case_subscriptions,
            self.subscribed_dockets,
        )
        result_str += f"{subs_made_str}\n"

        remaining_subs = all_subscriptions
        if self.num_big_case_subscriptions > 0:
            (
                big_case_subs,
                big_case_sub_str,
            ) = self.subscribe_randoms_to_group(
                self.big_cases_group,
                self.num_big_case_subscriptions,
                all_subscriptions,
            )
            result_str += f"{big_case_sub_str}\n"
            remaining_subs = list(set(all_subscriptions) - set(big_case_subs))

        if self.num_little_case_subscriptions > 0:
            _, little_case_sub_str = self.subscribe_randoms_to_group(
                little_cases_group,
                self.num_little_case_subscriptions,
                remaining_subs,
            )
            result_str += f"{little_case_sub_str}\n"
        return result_str

    def make_admin_users(self) -> str:
        """
        Made 1 admin user

        :return: a string saying that it was made
        :rtype: str
        """
        info = "Admin user(s)"
        AdminFactory.create_batch(self.NUM_ADMIN_USERS)
        return self._made_str(self.NUM_ADMIN_USERS, info)

    def make_big_cases_group_and_channels(
        self,
    ) -> tuple[Group | GroupFactory, str]:
        """
        Make 1 big cases Group and 2 channels for it (Mastodon and Twitter)

        :return: the big cases Group, a string saying that they were made
        :rtype: (Group, str)
        """
        info = "Big Cases Group and the Mastodon and Twitter Channels"
        big_cases_group = self._make_group_and_2_channels(True, "Big cases")
        return big_cases_group, self._made_str(self.NUM_BIGCASES_GROUPS, info)

    def make_little_cases_group_and_channels(
        self,
    ) -> tuple[Group | GroupFactory, str]:
        """
        Make 1 little cases Group and 2 channels for it (Mastodon and Twitter)

        :return: the little cases Group, a string saying that they were made
        :rtype: (Group, str)
        """
        info = "Little Cases Group and the Mastodon and Twitter Channels"
        little_cases_group = self._make_group_and_2_channels(
            False, "Little cases"
        )
        return little_cases_group, self._made_str(
            self.NUM_LITTLECASES_GROUPS, info
        )

    def make_subscriptions(
        self,
        random_num: int = (DEFAULT_NUM_BIG_CASES + DEFAULT_NUM_LITTLE_CASES),
        docket_ids: list[int] | None = None,
    ) -> tuple[list[Subscription | SubscriptionFactory], str]:
        """
        Make subscriptions: Make [random_num] random subscriptions.
        If there are any docket_ids, make subscriptions from those CL docket ids.

        Return all subscriptions and a string saying how many where made.

        :param: random_num The number of random subscriptions to create.
          Default = 5
        :type: int
        :param: docket_ids A list of ids of dockets to get from CourtListener.
          Default = None
        :type: list[int] | None
        :return: the list of subscriptions created, a string with the number of
        random subscriptions made
        :rtype: (list[Subscription], str)
        """
        subs_made = []
        result_strs = []
        if (docket_ids is not None) and len(docket_ids) > 0:
            cl_docket_subs, cl_docket_str = self.make_subs_from_cl_docket_ids(
                docket_ids
            )
            subs_made.extend(cl_docket_subs)
            result_strs.append(cl_docket_str)

        if random_num > 0:
            random_subs, random_made_str = self.make_random_subscriptions(
                random_num
            )
            subs_made.extend(random_subs)
            result_strs.append(random_made_str)

        return subs_made, "\n".join(result_strs)

    def make_subs_from_cl_docket_ids(
        self, docket_ids: list[int] | None = None
    ) -> tuple[list[Subscription | SubscriptionFactory], str]:
        """
        Makes subscriptions from CourtListener dockets with the given
        docket_ids.
        Subscribe them all to the big_cases Group

        :param docket_ids:
        :returns: the list of Subscriptions made, string saying how many
        were made
        :rtype: (list[Subscription], str)
        """
        info = "Real subscription(s) (Big cases) from CL docket ids"
        if docket_ids is None:
            return [], self._made_str(0, info)

        subs = []
        num = len(docket_ids)
        if self.big_cases_group is not None:
            big_cases_channels = self.big_cases_group.channels.all()
        else:
            big_cases_channels = None

        for docket_id in docket_ids:
            docket = lookup_docket_by_cl_id(docket_id)
            subscription = SubscriptionFactory(
                cl_docket_id=docket_id,
                docket_number=docket["docket_number"],
                docket_name=docket["case_name"],
                cl_court_id=docket["court_id"],
                pacer_case_id=docket["pacer_case_id"],
                cl_slug=docket["slug"],
                channels=big_cases_channels,
            )
            subs.append(subscription)

        return subs, self._made_str(
            num,
            f"{info} {docket_ids}",
        )

    def make_random_subscriptions(
        self, num: int = 5
    ) -> tuple[list[Subscription | SubscriptionFactory], str]:
        """
        Make [num] subscriptions with randomly generated info.
        Default num = 5

        :returns: the list of Subscriptions made, string saying how many
        were made
        :rtype: (list[Subscription], str)
        """
        info = "Subscriptions (random)"
        if num < 1:
            return [], self._made_str(0, info)
        else:
            return SubscriptionFactory.create_batch(num), self._made_str(
                num, info
            )

    def subscribe_randoms_to_group(
        self,
        group: Group | GroupFactory,
        num: int = 3,
        subscriptions: list[Subscription | SubscriptionFactory] | None = None,
    ) -> tuple[list[Subscription | SubscriptionFactory], str]:
        """
        Pick {num} random subscriptions and add them to given group

        :returns: the list of subscriptions subscribed to the group,
          a string saying that the subscriptions were subscribed
        :rtype: (list[Subscription],str)
        """
        group_str = f"group ([{group.id}] {group.name})"
        info = f"subscriptions subscribed to {group_str}"
        if (subscriptions is None) or num == 0:
            return [], self._made_str(0, info)

        subscribed_subs = []
        random_subs = fake.random_elements(
            subscriptions, length=num, unique=True
        )

        for sub in random_subs:
            for channel in group.channels.all():
                sub.channel.add(channel)
            subscribed_subs.append(sub)

        return subscribed_subs, self._made_str(
            num,
            info,
        )

    @staticmethod
    def _make_group_and_2_channels(
        is_big_cases: bool = False, name: str | None = None
    ) -> Group | GroupFactory:
        if name is None:
            new_cases_group = GroupFactory.create(is_big_cases=is_big_cases)
        else:
            new_cases_group = GroupFactory.create(
                name=name, is_big_cases=is_big_cases
            )
        mastodon_ch = ChannelFactory.create(
            mastodon=True, group=new_cases_group
        )
        twitter_ch = ChannelFactory.create(twitter=True, group=new_cases_group)
        new_cases_group.channels.add(mastodon_ch)
        new_cases_group.channels.add(twitter_ch)
        return new_cases_group

    @staticmethod
    def _made_str(num: int = 1, info: str = "") -> str:
        return f"   {num} {info}"
