import pandas as pd
import numpy as np
import re
import time

# TODO 1: some tool


def filter_data(df, target_index, col_name):
    ind = []
    for item in df[col_name]:
        if item in target_index:
            ind.append(True)
        else:
            ind.append(False)
    return df.iloc[ind,]


def pivot_table(df, co_list, ind_list):
    df = filter_data(df, co_list, 'participant_name')
    df = filter_data(df, ind_list, 'indicator')
    # col = ['participant_name','indicator','indicator_description','Top 1 Relevant Sent','keynumber_1','Completeness']
    col = ['participant_name', 'indicator', 'Completeness']
    df = df[col]
    return df


# TODO 2: Extraction Functions


def cleaning(data):
    """
    clean the text
    """
    df1 = data[['corp_id', 'file_name']]

    for i in range(len(df1)):
        #   t_str=re.sub(r'\\u[a-z0-9]{4}','',data.translation[i].encode('unicode_escape').decode())
        t_str = str(data.translation[i])
        t_str = re.sub(r'&#[0-9]+;', '', t_str)
        t_str = re.sub(r'&amp;', '&', t_str)
        t_str = re.sub(r'&lt;', '<', t_str)
        t_str = re.sub(r'&gt;', '>', t_str)
        t_str = re.sub(r'&quot;', '"', t_str)
        t_str = re.sub(r'\\x[a-zA-Z0-9]{2}', '"', t_str)
        t_str = t_str.replace('\\t', ' ').replace(" + ", ' ')

        t_str = re.sub(r'[\f\r\t\v\n]', '', t_str)

        t_str = t_str.lower()
        df1.loc[i, 'text'] = t_str

    return df1


def indicator_texttofilter(path):
    """
    turn txt to 3-criterion-filter
    """
    indicator = pd.read_table(path,delim_whitespace=True,names=("indicator", "criterion1", "criterion2", "criterion3"))
    indicator.criterion1 = [re.sub(',', '|', x) for x in indicator.criterion1]
    indicator.criterion2 = [re.sub(',', '|', x) if pd.notna(x) else "" for x in indicator.criterion2]
    indicator.criterion3 = [re.sub(',', '|', x) if pd.notna(x) else "" for x in indicator.criterion3]
    indicator.criterion1 = ['(?=.*' + x + ')' for x in indicator.criterion1]
    indicator.criterion2 = ['(?=.*' + x + ')' if x != '' else "" for x in indicator.criterion2]
    indicator.criterion3 = ['(?=.*' + x + ')' if x != '' else "" for x in indicator.criterion3]

    return indicator


def relevantsent_extract(cleaned_text, indicator_filter, start=0, end=10):
    df = pd.DataFrame(columns=['corp_id', 'file_name', 'indicator', 'sentence', 'length'])

    start_time = time.time()

    # for i in range(len(df1)):
    for i in range(start,end):
        sents = cleaned_text.loc[i, 'text']
        sent = re.split(r'(?<!\d)\.(?!\d)', sents)
        sent_1stfilter = []
        for s in sent:
            if re.findall(r'[materiality|sustainability|management|governance|impacts|risks|fraud|stakeholder|economic|revenue|community|tax|public|research|r&d|supply|energy|water|emmission|waste|recycle|supplie|consumption|ghg|intensity|biodiversity|occupational|health|employee|fair|equal|gender|social|community|supplier|local|engagement]',s):
                sent_1stfilter.append(s)

        for s in sent_1stfilter:
            for j in range(len(indicator_filter)):
                rc = indicator_filter.criterion1[j] + indicator_filter.criterion2[j] + indicator_filter.criterion3[j]

                recompile = re.compile(rc)

                if re.findall(recompile, s):
                    # ['corp_id','file_name','indicator','sentence','number']
                    df = df.append({'corp_id': cleaned_text.corp_id[i], 'file_name': cleaned_text.file_name[i],
                                    'indicator': indicator_filter.indicator[j], 'sentence': s,
                                    'length': len(s)}, ignore_index=True)

    print("--- %s seconds ---" % (time.time() - start_time))

    return df


def number_extract(sent_df):
    df_num = pd.DataFrame(columns=['corp_id', 'file_name', 'indicator', 'sentence', 'sent_clean', 'number'])
    num_indicator = ['\bone(\b|-)', 'two(\b|-)', 'three', 'four', 'five', 'six', 'seven', 'eight', '\bnine(\b|-)',
                     '\bten(\b|-)', \
                     'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', \
                     'eighteen', 'nineteen', 'twenty', 'thirty', 'forty', 'fifty']
    num_join = "|".join(num_indicator)
    num_compile = re.compile(
        r'((?:' + num_join + ')|\s\d+(?:,\d+)?(?:\.\d+)?)(?:\s*(mln|million|bln|billion|thousand|hundred|%|percent|' + num_join + '))?|' + num_join)

    month = "January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec"
    month = month.lower()
    Date_compile = re.compile(r'(\d{1,2}\s*(?:' + month + ')(?:\s|$))|(\d{1,2}(?:\/|-)\d{1,2}((?:\/|-)\d{2,4})?)')
    year_compile = re.compile(r'(19|20)[0-9]{2}')
    order_compile = re.compile(r'\s[0-9][.]\s|\s[0-9]\)\s*')
    note_compile = re.compile(r'(group)*(note(s)*\s{0,}[0-9]+)')

    for i in range(len(sent_df)):

        string = sent_df.loc[i, 'sentence']

        string = re.sub(Date_compile, '', string)
        string = re.sub(year_compile, '', string)
        string = re.sub(note_compile, '', string)
        string = re.sub(order_compile, '', string)

        find_all = []
        for match in num_compile.finditer(string):
            find_all.append(match[0])

        if find_all:
            df_num = df_num.append({'corp_id': sent_df.corp_id[i], 'file_name': sent_df.file_name[i],
                                    'indicator': sent_df.indicator[i], 'sentence': sent_df.loc[i, 'sentence'],
                                    'sent_clean': string, 'number': ' |&| '.join(find_all)}, ignore_index=True)
    for i in range(len(df_num)):
        find_all = []
        for match in year_compile.finditer(df_num.sentence[i]):
            find_all.append(match[0])
        if find_all:
            df_num.loc[i, 'year_info'] = ' |&| '.join(np.unique(find_all))

    return df_num


def novalue_sent(sent_df, num_df):
    df_nonumber = pd.DataFrame(pd.concat([sent_df.iloc[:, :4], num_df.iloc[:, :4]]).drop_duplicates(keep=False))

    df_nonumber_list = df_nonumber.iloc[:, :3].drop_duplicates(keep='first')
    df_nonumber_list = df_nonumber_list.reset_index(drop=True)
    df_nonumber_list.columns = ['cop_file_id', 'file_name', 'indicator']
    df_nonumber_list.cop_file_id = df_nonumber_list.cop_file_id.apply(int)

    df_nonumber_list['non_number'] = True

    return df_nonumber_list


def extract_bycompany(cop_file_id, file_name, df_num):
    sample = df_num.loc[(df_num.corp_id == cop_file_id) & (df_num.file_name == file_name),]
    sample = sample.reset_index(drop=True)

    sent_count = pd.DataFrame(sample.sentence.value_counts())
    sent_count.columns = ['labels']
    sample = pd.merge(sample, sent_count, left_on='sentence', right_index=True)

    num_indicator_2 = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', \
                       'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', \
                       'eighteen', 'nineteen', 'twenty', 'thirty', 'forty', 'fifty']
    num_join_2 = '|'.join(num_indicator_2)

    single_digit = re.compile(r'^\s*\d\s*$')
    alpha = re.compile(r'^\s*(' + num_join_2 + ')\s*$')

    for i in range(len(sample)):
        if not sample.indicator[i].startswith('D'):

            lst = sample.number[i].split(' |&| ')
            lst_score = []

            for x in lst:
                if re.match(single_digit, x):
                    lst_score.append(1)
                elif re.match(alpha, x):
                    lst_score.append(2)
                else:
                    lst_score.append(3)

            sample.loc[i, 'score'] = sum(lst_score) / len(lst_score)

        else:

            lst = sample.number[i].split(' |&| ')
            lst_score = []

            for x in lst:
                if re.match(single_digit, x):
                    lst_score.append(1)
                elif re.match(alpha, x):
                    lst_score.append(3)
                else:
                    lst_score.append(2)

            sample.loc[i, 'score'] = sum(lst_score) / len(lst_score)

    sample['year_score'] = [2 if (x == '2016') or (str(x) == 'nan') else 1 for x in sample.year_info]
    sample['number_count'] = [x.count('|&|') + 1 for x in sample.number]

    return sample


def full_indicator_bycompany(extract_bycompany_df, cop_df, df_nonumber_list, cop_id, file_name):
    sample_result = pd.DataFrame(
        columns=['corp_id', 'file_name', 'indicator', 'indicator_description', '1st_choice', 'keynumber_1',
                 '2nd_choice', 'keynumber_2'])

    for i in extract_bycompany_df.indicator.unique():
        t = extract_bycompany_df.loc[extract_bycompany_df.indicator == i,]
        t = t.sort_values(['score', 'year_score', 'labels', 'number_count'], ascending=[False, False, True, False],
                          inplace=False)
        t = t.reset_index()

        sample_result = sample_result.append(
            {'corp_id': extract_bycompany_df.corp_id, 'file_name': extract_bycompany_df.file_name, \
             'indicator': i,
             'indicator_description': indicator_full.loc[indicator_full['index'] == i, 'indicator'].values[0], \
             '1st_choice': t.loc[0, 'sentence'], 'keynumber_1': t.loc[0, 'number'], \
             '2nd_choice': t.loc[1, 'sentence'] if len(t) > 1 else 'NA',
             'keynumber_2': t.loc[1, 'number'] if len(t) > 1 else 'NA'}, ignore_index=True)

    sample_result['keynumber_1'] = [re.sub(r'\s\|\&\|', ';', x) if str(x) != 'nan' else np.nan for x in
                                    sample_result['keynumber_1']]
    sample_result['keynumber_2'] = [re.sub(r'\s\|\&\|', ';', x) if str(x) != 'nan' else np.nan for x in
                                    sample_result['keynumber_2']]

    sample_table = pd.DataFrame(
        columns=['participant_name', 'country', 'organization_type', 'sector_name', 'cop_file_id', 'file_name',
                 'indicator', 'indicator_description', 'Mentioned'])
    sample_table[['indicator', 'indicator_description']] = indicator_full
    sample_table[['cop_file_id', 'file_name']] = [cop_id, file_name]

    sample_table[['participant_name', 'country', 'organization_type', 'sector_name']] = cop_df.loc[
        cop_df.cop_file_id == int(sample_table.cop_file_id[0]), ['participant_name', 'country', 'organization_type',
                                                                 'sector_name']].values

    sample_table['cop_file_id'] = sample_table['cop_file_id'].apply(int)
    sample_table = pd.merge(sample_table, df_nonumber_list, how='left',
                            left_on=['cop_file_id', 'file_name', 'indicator'],
                            right_on=['cop_file_id', 'file_name', 'indicator'])
    sample_table = pd.merge(sample_table,
                            sample_result[['indicator', '1st_choice', 'keynumber_1', '2nd_choice', 'keynumber_2']],
                            how='left', left_on='indicator', right_on='indicator')

    for x in range(len(sample_table)):
        if str(sample_table.loc[x, '1st_choice']) != 'nan':
            sample_table.loc[x, 'Mentioned'] = 2
        elif sample_table.loc[x, 'non_number'] == True:
            sample_table.loc[x, 'Mentioned'] = 1
        else:
            sample_table.loc[x, 'Mentioned'] = 0

    sample_table = sample_table.rename(index=str,
                                       columns={"Mentioned": "Completeness", "1st_choice": "Top 1 Relevant Sent",
                                                '2nd_choice': '2nd Relevant Sent'})

    sample_table = sample_table.fillna('NA')

    return sample_table


if __name__ == "__main__":

    # TODO 3: get target data for 2017
    data = pd.read_excel('unctad_2018_old.xlsx')
    target_name_2018 = list(set(data['participant_name'])); len(target_name_2018)
    data2017 = pd.read_excel('CO METADATA 2017 - cop_files_2017-forGlobalAI.xlsx')
    data2018 = pd.read_excel('CO MEDATA 2018 - cop_files_2018_08_17-forGlobalAI.xlsx')
    target_org_id = filter_data(data2018, target_name_2018,'participant_name')
    target_org = list(target_org_id['organization_id'])
    target_co_df = filter_data(data2017, target_org,'organization_id')
    file_id = list(target_co_df['cop_file_id']); len(file_id)
    target_name_2018 = list(set(data['participant_name']))

    data1 = pd.read_csv('Phase2.5_2017_p1_EN.csv')
    data2 = pd.read_csv('Phase2.5_2017_EN_p2.csv')
    data1_1 = filter_data(data1,file_id,'corp_id')
    data2_1 = filter_data(data2,file_id,'corp_id')
    data1_1.append(data2_1, ignore_index=True)
    data1_1 = data1_1.drop('Unnamed: 0',axis=1)
    data3 = pd.read_csv('Phase2.5_2017_p1.csv')
    data4 = pd.read_csv('Phase2.5_2017_p2.csv')
    data3_1 = filter_data(data3,file_id,'corp_id')
    data4_1 = filter_data(data4,file_id,'corp_id')
    data3_1 = data3_1.append(data4_1, ignore_index=True)
    ind = []
    for item in data3_1['translation']:
        if pd.isnull(item):
            ind.append(False)
        else: ind.append(True)
    data3_1 = data3_1.iloc[ind,]
    data1_1 = data1_1.append(data3_1, ignore_index=True)
    data1_1 = data1_1.drop_duplicates(keep='last')
    data1_1 = data1_1.drop_duplicates(subset='corp_id',keep = 'last')
    data1_1.to_csv('selected_2017_co.csv',index=False)
    data3 = pd.read_csv('Phase2.5_2017_p1.csv')
    data4 = pd.read_csv('Phase2.5_2017_p2.csv')
    data3_1 = filter_data(data3,file_id,'corp_id')
    data4_1 = filter_data(data4,file_id,'corp_id')
    data3_1 = data3_1.append(data4_1, ignore_index=True)
    ind = []
    for item in data3_1['translation']:
        if pd.isnull(item):
            ind.append(False)
        else: ind.append(True)
    data3_1 = data3_1.iloc[ind,]
    data1_1 = data1_1.append(data3_1, ignore_index=True)
    data1_1 = data1_1.drop_duplicates(keep='last')
    data1_1 = data1_1.drop_duplicates(subset='corp_id',keep = 'last')
    data1_1.to_csv('selected_2017_co.csv',index=False)


    # TODO 4: read rules
    indicator_full = pd.read_csv('wikirate_to_indicator.csv')
    indicator_full = indicator_full[['index','indicator']].drop_duplicates()
    indicator_full = indicator_full.iloc[:35,]

    cop_8 = pd.read_excel('CO MEDATA 2018 - cop_files_2018_08_17-forGlobalAI.xlsx')
    cop_7 = pd.read_excel('CO METADATA 2017 - cop_files_2017-forGlobalAI.xlsx')

    data2017 = pd.read_csv('selected_2017_co.csv')

    df1 = cleaning(data2017)
    path = 'wikirate indicator.txt'
    indicator_searchrule = indicator_texttofilter(path)
    sent_df = relevantsent_extract(df1, indicator_searchrule, start=2400, end=2483) # 2483
    sent_df.to_csv('sent_df_2017.csv', index=False)
    num_df = number_extract(sent_df)
    num_df.to_csv('num_df_2017.csv', index=False)
    file_id_list = [tuple(x) for x in sent_df[['corp_id', 'file_name']].drop_duplicates().values]
    cop_df = cop_7
    novalue_sent_df = novalue_sent(sent_df, num_df)
    all_tables = pd.DataFrame(columns=['participant_name', 'country', 'organization_type', 'sector_name',
                                       'cop_file_id', 'file_name', 'indicator', 'indicator_description',
                                       'Completeness', 'non_number', 'Top 1 Relevant Sent', 'keynumber_1',
                                       '2nd Relevant Sent', 'keynumber_2'])
    ind = []
    start = -1
    for i in file_id_list:
        print(start)
        try:
            smple = extract_bycompany(i[0], i[1], num_df)
            smple_table = full_indicator_bycompany(smple, cop_df, novalue_sent_df, i[0], i[1])

            all_tables = pd.DataFrame(pd.concat([all_tables, smple_table], ignore_index=True))
            start += 1
            ind.append(start)
        except:
            pass
    all_tables.to_csv('2017_result_2500.csv', index=False)

    data = all_tables
    print(data)
