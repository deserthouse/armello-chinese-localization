using System.Reflection;
using BepInEx;
using BepInEx.Logging;
using BepInEx.Unity.IL2CPP;
using HarmonyLib;

namespace ArmelloUrlFix;

[BepInPlugin(PluginGuid, PluginName, PluginVersion)]
public class UrlFixPlugin : BasePlugin
{
    public const string PluginGuid = "deserthouse.armello.urlfix";
    public const string PluginName = "Armello URL Tag Fix";
    public const string PluginVersion = "1.5.0";
    internal static ManualLogSource L;

    public override void Load()
    {
        L = base.Log;
        L.LogInfo("ArmelloUrlFix v" + PluginVersion + " loading");

        var harmony = new Harmony(PluginGuid);
        int patched = 0;

        var postfix = new HarmonyMethod(typeof(TextFix).GetMethod("FixWrapped"));
        foreach (var m in typeof(NGUIText).GetMethods(BindingFlags.Public | BindingFlags.Static))
        {
            if (m.Name == "WrapText")
            {
                try { harmony.Patch(m, postfix: postfix); patched++; }
                catch (System.Exception ex) { L.LogWarning("  WrapText: " + ex.Message); }
            }
        }

        L.LogInfo("ArmelloUrlFix: " + patched + " WrapText overload(s) patched");
    }
}

public static class TextFix
{
    /// <summary>
    /// WrapText 的 postfix：只修复被换行拆断的 [/url] 标签。
    /// v1.5 修复：正则必须要求 u、r、l 三个字母都在场，
    /// 不会误匹配 [/u]（下划线闭合标签）。
    /// </summary>
    public static void FixWrapped(ref string finalText)
    {
        if (string.IsNullOrEmpty(finalText)) return;
        if (!finalText.Contains("[/")) return;

        var original = finalText;

        // 只匹配 [/url] 且中间被 \n 拆断的变体
        // 必须同时含 u、r、l（可选 \n 插在任意位置）
        // 不会匹配 [/u]、[/ur]、[/] 等不完整序列
        finalText = System.Text.RegularExpressions.Regex.Replace(
            finalText,
            @"\[/u\nr\nl\]|\[/ur\nl\]|\[/u\nrl\]|\[/\nurl\]|\[\n/url\]",
            "[/url]"
        );

        if (finalText != original)
        {
            UrlFixPlugin.L?.LogInfo("[UrlFix] repaired split [/url]");
        }
    }
}
