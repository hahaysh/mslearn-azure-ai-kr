---
title: Azure 개발자를 위한 실습
permalink: index.html
layout: home
---

## <a id="overview"></a>개요

다음 실습에서는 Microsoft Azure 솔루션을 빌드하고 배포할 때 개발자가 수행하는 일반적인 작업을 직접 살펴봅니다.

> **참고**: 실습을 완료하려면 필요한 Azure 리소스를 프로비전할 수 있는 충분한 권한과 할당량이 있는 Azure 구독이 필요합니다. 구독이 없다면 [Azure 계정](https://azure.microsoft.com/free)에 등록할 수 있습니다.

모든 실습에서 사용하는 계정과 소프트웨어는 [실습 요구 사항]({{ site.github.url }}/lab-requirements.html)에서 확인합니다. 각 실습의 **시작하기 전에** 섹션에서도 해당 실습에 필요한 요구 사항을 확인할 수 있습니다.

## 주제 영역

{% assign exercises = site.pages | where_exp:"page", "page.url contains '/Instructions-kr/'" %}
{% assign grouped_exercises = exercises | group_by: "lab.topic" %}

<ul>
{% for group in grouped_exercises %}
<li><a href="#{{ group.name | slugify }}">{{ group.name }}</a></li>
{% endfor %}
</ul>

{% for group in grouped_exercises %}

## <a id="{{ group.name | slugify }}"></a>{{ group.name }}

{% for activity in group.items %}
[{{ activity.lab.title }}]({{ site.github.url }}{{ activity.url }}) <br/> {{ activity.lab.description }} <br/> <span class="meta-grey">수준: {{activity.lab.level}} &nbsp; &nbsp; 소요 시간: {{activity.lab.duration}}분</span>

---

{% endfor %}
<a href="#overview">맨 위로 돌아가기</a>
{% endfor %}
