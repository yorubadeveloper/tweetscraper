#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# !pip install GetOldTweets3
import getopt
import os
import re
import sys
import traceback

if sys.version_info[0] < 3:
    raise Exception("Python 2.x is not supported. Please upgrade to 3.x")

import GetOldTweets3 as got


def main(argv):
    if len(argv) == 0:
        print('You must pass some parameters. Use \"-h\" to help.')
        return

    if len(argv) == 1 and argv[0] == '-h':
        print(__doc__)
        return

    try:
        opts, args = getopt.getopt(argv, "", ("querysearch=",
                                              "username=",
                                              "usernames-from-file=",
                                              "since=",
                                              "until=",
                                              "near=",
                                              "within=",
                                              "toptweets",
                                              "maxtweets=",
                                              "lang=",
                                              "output=",
                                              "debug"))

        tweetCriteria = got.manager.TweetCriteria()
        outputFileName = "output_got.csv"

        debug = False
        usernames = set()
        username_files = set()
        for opt, arg in opts:
            if opt == '--querysearch':
                tweetCriteria.querySearch = arg

            elif opt == '--username':
                usernames_ = [u.lstrip('@') for u in re.split(r'[\s,]+', arg) if u]
                usernames_ = [u.lower() for u in usernames_ if u]
                usernames |= set(usernames_)

            elif opt == '--usernames-from-file':
                username_files.add(arg)

            elif opt == '--since':
                tweetCriteria.since = arg

            elif opt == '--until':
                tweetCriteria.until = arg

            elif opt == '--near':
                geocode = arg.split(',')
                try:
                    if len(geocode) != 2:
                        raise
                    lat, lon = geocode[0].strip(), geocode[1].strip()
                    if lat[-1].lower() == 'n':
                        lat = float(lat[:-1])
                    elif lat[-1].lower() == 's':
                        lat = -float(lat[:-1])
                    else:
                        lat = float(lat)

                    if lon[-1].lower() == 'e':
                        lon = float(lon[:-1])
                    elif lon[-1].lower() == 'w':
                        lon = -float(lon[:-1])
                    else:
                        lon = float(lon)
                    if lat < -180 or lat > 180:
                        raise
                    if lon < -90 or lon > 90:
                        raise
                    tweetCriteria.lat = lat
                    tweetCriteria.lon = lon
                except:
                    tweetCriteria.near = arg

            elif opt == '--within':
                tweetCriteria.within = arg

            elif opt == '--toptweets':
                tweetCriteria.topTweets = True

            elif opt == '--maxtweets':
                tweetCriteria.maxTweets = int(arg)

            elif opt == '--lang':
                tweetCriteria.lang = arg

            elif opt == '--output':
                outputFileName = arg

            elif opt == '--debug':
                debug = True

        if debug:
            print(' '.join(sys.argv))
            print("GetOldTweets3", got.__version__)

        if username_files:
            for uf in username_files:
                if not os.path.isfile(uf):
                    raise Exception("File not found: %s" % uf)
                with open(uf) as f:
                    data = f.read()
                    data = re.sub('(?m)#.*?$', '', data)  # remove comments
                    usernames_ = [u.lstrip('@') for u in re.split(r'[\s,]+', data) if u]
                    usernames_ = [u.lower() for u in usernames_ if u]
                    usernames |= set(usernames_)
                    print("Found %i usernames in %s" % (len(usernames_), uf))

        if usernames:
            if len(usernames) > 1:
                tweetCriteria.username = usernames
                if len(usernames) > 20 and tweetCriteria.maxTweets > 0:
                    maxtweets_ = (len(usernames) // 20 + (len(usernames) % 20 > 0)) * tweetCriteria.maxTweets
                    print("Warning: due to multiple username batches `maxtweets' set to %i" % maxtweets_)
            else:
                tweetCriteria.username = usernames.pop()

        outputFile = open(outputFileName, "w+", encoding="utf8")
        outputFile.write('date,username,to,replies,retweets,favorites,text,geo,mentions,hashtags,id,permalink\n')

        cnt = 0

        def receiveBuffer(tweets):
            nonlocal cnt

            for t in tweets:
                data = [t.date.strftime("%Y-%m-%d %H:%M:%S"),
                        t.username,
                        t.to or '',
                        t.replies,
                        t.retweets,
                        t.favorites,
                        '"' + t.text.replace('"', '""') + '"',
                        t.geo,
                        t.mentions,
                        t.hashtags,
                        t.id,
                        t.permalink]
                data[:] = [i if isinstance(i, str) else str(i) for i in data]
                outputFile.write(','.join(data) + '\n')

            outputFile.flush()
            cnt += len(tweets)

            if sys.stdout.isatty():
                print("\rSaved %i" % cnt, end='', flush=True)
            else:
                print(cnt, end=' ', flush=True)

        print("Downloading tweets...")
        got.manager.TweetManager.getTweets(tweetCriteria, receiveBuffer, debug=debug)

    except getopt.GetoptError as err:
        # print('Arguments parser error, try -h')
        print('\t' + str(err))
#         print("Downloading old tweets")

    except KeyboardInterrupt:
        print("\r\nInterrupted.\r\n")

    except Exception as err:
        print(traceback.format_exc())
        print(str(err))

    finally:
        if "outputFile" in locals():
            outputFile.close()
            print()
            print('Done. Output file generated "%s".' % outputFileName)


if __name__ == '__main__':
    main(sys.argv[1:])

    # os.system('GetOldTweets3 --querysearch "europe refugees" --maxtweets 1000 --output foolll.csv')
    # os.system('GetOldTweets3 --username "barackobama" --toptweets --maxtweets 10')

    os.system('GetOldTweets3 --username "ZenithBank" --since 2019-01-01 --until 2019-12-21 --output Zenith.csv')
    os.system('GetOldTweets3 --username "wemabank" --since 2019-01-01 --until 2019-12-21 --output Wema.csv')
    os.system('GetOldTweets3 --username "myaccessbank" --since 2019-01-01 --until 2019-12-21 --output Access.csv')
    os.system('GetOldTweets3 --username "gtbank" --since 2019-01-01 --until 2019-12-21 --output GTB.csv')
    os.system('GetOldTweets3 --username "FirstBankngr" --since 2019-01-01 --until 2019-12-21 --output FirstBank.csv')
    os.system('GetOldTweets3 --username "PolarisBankLtd" --since 2019-01-01 --until 2019-12-21 --output Polaris.csv')
    os.system('GetOldTweets3 --username "kudabank" --since 2019-01-01 --until 2019-12-21 --output Kudabank.csv')
    os.system('GetOldTweets3 --username "MyFCMB" --since 2019-01-01 --until 2019-12-21 --output FCMB.csv')
    os.system('GetOldTweets3 --username "ecobank_nigeria" --since 2019-01-01 --until 2019-12-21 --output Ecobank.csv')
    os.system('GetOldTweets3 --username "StanbicIBTC" --since 2019-01-01 --until 2019-12-21 --output StanbicIBTC.csv')
    os.system('GetOldTweets3 --username "UBAGroup" --since 2019-01-01 --until 2019-12-21 --output UBA.csv')
    os.system('GetOldTweets3 --username "Sterling_Bankng" --since 2019-01-01 --until 2019-12-21 --output Sterling.csv')
    os.system('GetOldTweets3 --username "fidelitybankplc" --since 2019-01-01 --until 2019-12-21 --output Fidelity.csv')
    os.system('GetOldTweets3 --username "UNIONBANK_NG" --since 2019-01-01 --until 2019-12-21 --output Unionbank.csv')
    os.system('GetOldTweets3 --username "keystonebankng" --since 2019-01-01 --until 2019-12-21 --output Keystone.csv')
    os.system('GetOldTweets3 --username "UnityBankPlc" --since 2019-01-01 --until 2019-12-21 --output UnityBank.csv')

     
    # os.system('GetOldTweets3 --querysearch "#NigeriaDecides"--since 2015-03-01 --until 2015-03-31-- NigeriaDecides.csv')

    # os.system('GetOldTweets3 --querysearch "barackobama" --since 2015-09-10 --until 2015-09-12 --maxtweets 10 --output obama.csv')
    # os.system('GetOldTweets3 --querysearch "bitcoin" --lang cn - -maxtweets 10')
    # os.system('GetOldTweets3 --querysearch "bitcoin" --near "Berlin, Germany" --within 25 km --maxtweets 10')
    # os.system('GetOldTweets3 --querysearch "museum" --near "55.75, 37.61" - -within  km - -maxtweets 10')



