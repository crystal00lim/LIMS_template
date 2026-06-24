from django.shortcuts import render
from django.db.models import Count, Q
from .models import Culture, Isolate, Kb, Participant, WGS
from django.db.models.functions import TruncMonth, TruncDate
from django.utils import timezone
from collections import defaultdict
from django.apps import apps

def get_participant():
    # This gets all participants who are active in the study, and groups them into control or experimental (doxycycline)
    activeExperimental = Participant.objects.filter(status=True).filter(treatment=True)
    activeExperimental = [item.id for item in activeExperimental]

    activeControl = Participant.objects.filter(status=True).filter(treatment=False)
    activeControl = [item.id for item in activeControl]

    partner = Participant.objects.filter(status=True).filter(participant_type=False)
    partner = [item.id for item in partner]

    context = {
        'experimental': activeExperimental,
        'control': activeControl,
        'partner': partner
    }
    # print(context)
    return {'participant': context}

def get_participant_pie():
    participants = get_participant()
    participants = participants['participant']
    label = list(participants.keys())
    context = {'label': label}
    series = []

    for item in label:
        series.append(len(participants[item]))

    context.update({'series': series})

    # print(context)

    return {'breakdown': context}

def get_pos():
    # This calculates the percent of positive participants per visit and formats it ready for graphing
    participants = get_participant()
    participants = participants['participant']

    sample_types = ['nas_sa', 'phar_sa', 'rec_sa']
    totalVisit = (Culture.objects.values('visit_num').distinct().order_by('visit_num'))
    totalVisit = [item['visit_num'] for item in totalVisit]
    # print(totalVisit)

    queryset = {'visit': totalVisit}

    sample_filter = Q()
    for i in sample_types:
        column_name = i.lower() 
        sample_filter |= Q(**{column_name: True})
    participant_ids = Q()
    for group in list(participants.keys()):
        participant_ids |= Q(participant_id_id__in=participants[group])
    # print(sample_filter)
    # print(participant_ids)

    all_positives = Culture.objects.filter(
        sample_filter,
        participant_ids,
        visit_num__in=totalVisit
    ).values('participant_id_id', 'visit_num')
    # print(all_positives)

    total = (Culture.objects.filter(participant_id_id__in=participants['control']).values('visit_num').annotate(count=Count('id')).order_by('visit_num'))
    totalcontrol = [item['count'] for item in total]
    total = (Culture.objects.filter(participant_id_id__in=participants['experimental']).values('visit_num').annotate(count=Count('id')).order_by('visit_num'))
    totalexperimental = [item['count'] for item in total]
    total = (Culture.objects.filter(participant_id_id__in=participants['partner']).values('visit_num').annotate(count=Count('id')).order_by('visit_num'))
    totalpartner = [item['count'] for item in total]

    total = {
        'control': totalcontrol,
        'experimental': totalexperimental,
        'partner': totalpartner
    }
    # print(total)

    key = list(total.keys())
    # print(key)

    for item in key:
        while len(total[item]) < len(totalVisit):
            total[item].append(0)
    # print(total)

    positive_map = {(item['visit_num'], item['participant_id_id']) for item in all_positives}
    # print(positive_map)

    for label, pids in participants.items():
        series = []
        pid_set = set(pids)
    
        for v_num in totalVisit:
            count = sum(1 for pid in pids if (v_num, pid) in positive_map)
            # print(count)
            if count > 0:
                count /= total[label][v_num - 1]
                count *= 100
            else:
                count = 0
            series.append(round(count))
    
        queryset.update({label: series})
    # print(queryset)

    return {'participant': queryset}

def mrsa_resistance():
    participants = get_participant()
    participants = participants['participant']

    sample_types = ['Nas_SA', 'Phar_SA', 'Rec_SA']
    totalVisit = (Culture.objects.values('visit_num').distinct().order_by('visit_num'))
    totalVisit = [item['visit_num'] for item in totalVisit]

    queryset = {'visit': totalVisit}

    resistance = {
        'cefoxitin__lte': 21
    }

    participant_ids = Q()
    for group in list(participants.keys()):
        participant_ids |= Q(isolate_num__timepoint_id__participant_id_id__in=participants[group])

    all_res = Kb.objects.filter(
        participant_ids,
        isolate_num__timepoint_id__visit_num__in=totalVisit,
        **resistance
    ).values('isolate_num__timepoint_id__participant_id_id', 'isolate_num__timepoint_id__visit_num', 'isolate_num__sample_type')
    # print(all_res)

    mastertotal = {}
    for i in sample_types:
        total = (Kb.objects.filter(isolate_num__timepoint_id__participant_id_id__in=participants['control'], isolate_num__sample_type=i).values('isolate_num__timepoint_id__visit_num').annotate(count=Count('id'))).order_by('isolate_num__timepoint_id__visit_num')
        totalcontrol = [item['count'] for item in total]
        total = (Kb.objects.filter(isolate_num__timepoint_id__participant_id_id__in=participants['experimental'], isolate_num__sample_type__icontains=i).values('isolate_num__timepoint_id__visit_num').annotate(count=Count('id'))).order_by('isolate_num__timepoint_id__visit_num')
        totalexperimental = [item['count'] for item in total]
        total = (Kb.objects.filter(isolate_num__timepoint_id__participant_id_id__in=participants['partner'], isolate_num__sample_type__icontains=i).values('isolate_num__timepoint_id__visit_num').annotate(count=Count('id'))).order_by('isolate_num__timepoint_id__visit_num')
        totalpartner = [item['count'] for item in total]
        # print(i, ": ", totalexperimental)

        total = {
            'control': totalcontrol,
            'experimental': totalexperimental,
            'partner': totalpartner
        }
        key = list(total.keys())
        for item in key:
            while len(total[item]) < len(totalVisit):
                total[item].append(0)
            mastertotal.update({i: total})
    # print(mastertotal)

    resistance_map = {(item['isolate_num__timepoint_id__visit_num'], item['isolate_num__timepoint_id__participant_id_id'], item['isolate_num__sample_type']) for item in all_res}
    # print(positive_map)

    context = defaultdict(dict)
    for label, p in participants.items():
        for s in sample_types:
            n = [] 
            for v in totalVisit:
                count = sum(1 for pid in p if (v, pid, s) in resistance_map)
                try:
                    if count > 0:
                        total = mastertotal[s][label][v - 1]
                        if total > 0:
                            count = (count / total) * 100
                        else:
                            count = 0
                    else:
                        count = 0
                except (KeyError, IndexError):
                    count = 0
                n.append(round(count))
            context[s][label] = n
    context = dict(context)
    # print(context)

    label = ['control', 'experimental'] # temporary until we have more partners
    mrsa = {}
    for l in label:
        for s in sample_types:
            mrsa[f"{s}_{l}"] = {'id': f"{s}_{l}", 'title': f"{s} MRSA resistance in {l} Group", 'series': context[s][l][:7], 'col': mastertotal[s][l][:7], 'xlabel': totalVisit}
    # print(mrsa)
    return {'MRSA': mrsa}

def get_treedata():
    tree = []
    
    total_collections = Culture.objects.count()
    tree.append(total_collections)

    sites_data = {
        "root_total": total_collections  
    }
    sites = ['Nas', 'Phar', 'Rec']

    for s in sites:
        sample_filter = f"{s.lower()}_sa"

        tdata = Culture.objects.filter(**{f"{sample_filter}__isnull": False}).count()
        pdata = Isolate.objects.filter(sample_type__iexact=sample_filter).count()
        kdata = Kb.objects.filter(isolate_num__sample_type__iexact=sample_filter).count()
        sdata = WGS.objects.filter(isolate_num__sample_type__iexact=sample_filter).count()
        ndata = tdata - pdata
        tree.extend([tdata, pdata, kdata, sdata, ndata])

        sites_data[s] = {
            "total": tdata,
            "pos_sa": pdata,
            "neg_sa": ndata,
            "kb": kdata,
            "seq": sdata
        }

    if "Rec" in sites_data:
        sites_data["Rec"].update({
            "wgs_sa": sites_data["Rec"]["seq"],
            "pos_ma": Culture.objects.filter(rec_mac=1).count(),
            "neg_ma": Culture.objects.filter(rec_mac=0).count(),
            "pos_e": Culture.objects.filter(rec_esbl=1).count(),
            "neg_e": Culture.objects.filter(rec_esbl=0).count(),
            "wgs_e": WGS.objects.filter(isolate_num__sample_type='Rec_ESBL').count()
        })

    def build_hierarchical_tree(data_source):
        standard_sites = ["Nas", "Phar"]
        children_branches = [
            {
                'name': f"{'Nasal' if s == 'Nas' else 'Pharyngeal'}<br>{data_source[s]['total']}",
                'children': [
                    {
                        'name': f"Positive<br>{data_source[s]['pos_sa']}",
                        'children': [
                            {
                                'name': f"KB<br>{data_source[s]['kb']}",
                                'children': [
                                    {
                                        'name': f"WGS<br>{data_source[s]['seq']}",
                                    }
                                ]
                            }
                        ]
                    }, 
                    {"name": f"Negative<br>{data_source[s]['neg_sa']}"},
                ]
            }
            for s in standard_sites if s in data_source
        ]

        if "Rec" in data_source:
            r_data = data_source["Rec"]
            children_branches.append({
                "name": f"Rectal<br>{r_data['pos_sa'] + r_data['neg_sa']}",
                "children": [
                    {
                        "name": f"SA Pos<br>{r_data['pos_sa']}",
                        "children": [
                            {
                                "name": f"KB<br>{r_data['kb']}",
                                "children": [{"name": f"WGS<br>{r_data['wgs_sa']}"}]
                            }
                        ]
                    },
                    {"name": f"SA Neg<br>{r_data['neg_sa']}"},
                    {
                        "name": f"ESBL Pos<br>{r_data['pos_e']}",
                        "children": [{"name": f"WGS<br>{r_data['wgs_e']}"}]
                    },
                    {"name": f"ESBL Neg<br>{r_data['neg_e']}"},
                    {"name": f"Mac Pos<br>{r_data['pos_ma']}"},
                    {"name": f"Mac Neg<br>{r_data['neg_ma']}"},
                ]
            })

        return {
            "name": f"Total Collection<br>{data_source.get('root_total', 0)}",
            "children": children_branches
        }

    final_tree_layout = build_hierarchical_tree(sites_data)
    
    return {
        'tree_data': final_tree_layout,
        'flat_list_backup': tree
    }

def get_sequence_type():
    # trust = WGS.objects.filter(need_resequencing=False).values('organism', 'sequence_type')
    # print(trust)

    # trust_org = {(item['organism'], item['sequence_type']) for item in trust}
    # trust_org = {item['organism']: WGS.objects.filter(need_resequencing=False, organism=item['organism']).count() for item in trust}
    # print(trust_org)
    # unique_org = list({organism for organism, seq_type in trust_org})
    # print(unique_org)

    trust = WGS.objects.filter(need_resequencing=False).values('organism', 'sequence_type').annotate(count=Count('id')).order_by('organism', 'sequence_type')
    # print(trust)

    org = []
    for i in trust:
        org.append({'organism': i['organism'], 'seq_type': i['sequence_type'], 'count': i['count']})
    # print(org)

    final = {}
    for b in org:
        name = b['organism']
        data = {
            'x': b['seq_type'],
            'y': b['count']
        }
        if name not in final:
            final[name] = []

        final[name].append(data)

    query = [
        {'name': name, 'data': data}
        for name, data in final.items()
    ]
    print(query)
        
    return {
        'trust': final
    }
    
# Create your views here.
def dashboard(request):
    app_config = apps.get_app_config('doxypep')
    multiline = get_pos()
    multiline = multiline['participant']
    visit = multiline['visit']
    del multiline['visit']

    percentPos = {
        'xlabel': visit,
        'series': multiline,
        'title': 'Percent Positive Over Visit Number'
    }

    participantPie = get_participant_pie()
    participantPie = participantPie['breakdown']
    participantPie.update({'title': 'Participant Type Breakdown'})
    print(participantPie)

    mrsa = mrsa_resistance()
    mrsa = mrsa['MRSA']
    # print(mrsa)

    tree = get_treedata()
    tree_data = tree['tree_data']

    trust = get_sequence_type()
    trust = trust['trust']
    tree = {'series': trust}
    print(tree)

    return render(
        request, 
        'doxypep-dashboard.html', 
        {
            'app_name': app_config.verbose_name,
            'multiline': percentPos, 
            'participantPie': participantPie, 
            'MRSA_data': mrsa,
            'tree_data': tree_data,
            'trust': tree
        }
    )