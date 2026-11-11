#include<pybind11/pybind11.h>
#include<iostream>
#include<string>
#include<fstream>
#include<vector>
#include<utility>
#include<cstdlib>
#include<ctime>

namespace py = pybind11;
using namespace std;

int money = 0,week = 1;

void first();
int IsAcc(string acc,string pwd);
bool RegisterAcc(string acc,string pwd);
void input_save(string acc);
int getweek();
int getmoney();

void first()
{
	srand(time(0));
	ofstream fout("OI-Data/Acc.LongLong");
	fout<<1<<'\n';
    fout<<"baishengyuan"<<' '<<"bai123456"<<'\n';
    fout.close();
    fout.open("OI-Data/baishengyuan.Gay");
    fout<<"M: "<<1000000000<<'\n';
    fout<<"W: "<<1<<'\n';
    fout.close();
}

int IsAcc(string acc,string pwd)
{
    ifstream fin("OI-Data/Acc.LongLong");
    if(!fin.is_open())
	{
		first();
		fin.open("OI-Data/Acc.LongLong");
	}
    int n;
	if(!(fin>>n)) { fin.close(); return 2; }
    for(int i=1; i<=n; i++)
    {
        string in_acc,in_pwd;
        fin>>in_acc>>in_pwd;
        if(in_acc == acc)
        {
        	fin.close();
            if(in_pwd != pwd)	
				return 0;
			input_save(in_acc);
            return 1;
        }
    }
    fin.close();
    return 2;
}

bool RegisterAcc(string acc,string pwd)
{
    ifstream fin("OI-Data/Acc.LongLong");
    if(!fin.is_open())
	{
		first();
		fin.open("OI-Data/Acc.LongLong");
	}
    vector<pair<string,string>> users;
    int n;
    if(!(fin>>n)) { fin.close(); return false; }
    bool exist = false;
    for (int i=1; i<=n; i++)
    {
        string a,p;
        if(!(fin>>a>>p)) { fin.close(); return false; }
        if(a == acc)
        {
            exist = true;
            break;
        }
        users.emplace_back(a,p);
    }
    fin.close();
    if(exist) return false;

    ofstream fout("OI-Data/Acc.LongLong");
    if(!fout.is_open()) return false;
    fout<<users.size()+1<<'\n';
    for(auto &u : users)
        fout<<u.first<<' '<<u.second<<'\n';
    fout<<acc<<' '<<pwd<<'\n';
    fout.close();
    fout.open("OI-Data/"+acc+".Gay");
    fout<<"M: "<<0<<'\n';
    fout<<"W: "<<1<<'\n';
    fout.close();
    return true;
}

void input_save(string acc)
{
	ifstream fin("OI-Data/"+acc+".Gay");
	string tmp; money = 0,week = 1;
	fin>>tmp>>money>>tmp>>week;
}

int getweek() { return week; }

int getmoney() { return money; }

PYBIND11_MODULE(KimiTools,m)
{
    m.def("IsAcc",&IsAcc);
    m.def("RegisterAcc",&RegisterAcc);
    m.def("week",&getweek);
    m.def("money",&getmoney);
}
